const fs = require('node:fs/promises');
const path = require('node:path');
const matter = require('gray-matter');
const MarkdownIt = require('markdown-it');

const root = path.resolve(__dirname, '..');
const contentDirectory = path.join(root, 'content', 'news');
const outputDirectory = path.join(root, 'dist');
const allowedCategories = new Set(['予防接種', '休診・診療時間', '健康診断', '診療案内']);
const markdown = new MarkdownIt({ html: false, linkify: true, typographer: false });
const copiedPaths = ['index.html', 'assets', 'css', 'js', 'services', 'about', 'access', 'faq'];
const startMarker = '<!-- CMS:NEWS:START -->';
const endMarker = '<!-- CMS:NEWS:END -->';

const escapeHtml = (value) => String(value)
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')
  .replace(/'/g, '&#39;');

function formatDate(value, fieldName, filename) {
  if (value === undefined || value === null || value === '') return null;
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(value));
  if (!match) {
    throw new Error(`${filename}: ${fieldName} must use YYYY-MM-DD.`);
  }
  const [year, month, day] = match.slice(1).map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));
  if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) {
    throw new Error(`${filename}: ${fieldName} must be a real calendar date.`);
  }
  return String(value);
}

function requiredString(value, name, filename) {
  if (typeof value !== 'string' || !value.trim()) throw new Error(`${filename}: ${name} is required.`);
  return value.trim();
}

function validateArticle(data, body, filename, rawPublishedAt) {
  const title = requiredString(data.title, 'title', filename);
  const slug = requiredString(data.slug, 'slug', filename);
  const category = requiredString(data.category, 'category', filename);
  const publishedAt = formatDate(rawPublishedAt === undefined ? data.publishedAt : rawPublishedAt, 'publishedAt', filename);
  const sortOrder = data.sortOrder;
  if (!/^[a-z0-9-]+$/.test(slug)) throw new Error(`${filename}: invalid slug.`);
  if (path.basename(filename, '.md') !== slug) throw new Error(`${filename}: filename and slug must match.`);
  if (!allowedCategories.has(category)) throw new Error(`${filename}: invalid category.`);
  if (!body.trim()) throw new Error(`${filename}: body is required.`);
  if (markdown.parse(body, {}).some((token) => token.type === 'heading_open' && token.tag === 'h1')) {
    throw new Error(`${filename}: Markdown body must not contain an h1.`);
  }
  if (!publishedAt && (typeof sortOrder !== 'number' || !Number.isFinite(sortOrder))) {
    throw new Error(`${filename}: sortOrder is required when publishedAt is absent.`);
  }
  if (sortOrder !== undefined && (typeof sortOrder !== 'number' || !Number.isFinite(sortOrder))) {
    throw new Error(`${filename}: sortOrder must be a number.`);
  }
  return { title, slug, category, publishedAt, sortOrder, body };
}

function rawFrontMatterValue(source, fieldName) {
  const frontMatter = /^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/.exec(source);
  if (!frontMatter) return undefined;
  const field = new RegExp(`^${fieldName}:\\s*(.*?)\\s*$`, 'm').exec(frontMatter[1]);
  if (!field) return undefined;
  const rawValue = field[1].trim();
  const quoted = /^(['"])(.*)\1$/.exec(rawValue);
  return quoted ? quoted[2] : rawValue;
}

function articleOutputPath(slug) {
  return path.posix.join('news', `${slug}.html`);
}

async function readArticles() {
  const filenames = (await fs.readdir(contentDirectory)).filter((name) => name.endsWith('.md')).sort();
  if (!filenames.length) throw new Error('content/news must contain Markdown files.');
  const articles = await Promise.all(filenames.map(async (filename) => {
    const source = await fs.readFile(path.join(contentDirectory, filename), 'utf8');
    const parsed = matter(source);
    return validateArticle(parsed.data, parsed.content, filename, rawFrontMatterValue(source, 'publishedAt'));
  }));
  const slugs = new Set();
  const outputPaths = new Set(['news/index.html']);
  for (const article of articles) {
    if (slugs.has(article.slug)) throw new Error(`Duplicate slug: ${article.slug}`);
    slugs.add(article.slug);
    article.outputPath = articleOutputPath(article.slug);
    if (outputPaths.has(article.outputPath)) throw new Error(`Output path collision: ${article.outputPath}`);
    outputPaths.add(article.outputPath);
  }
  return articles.sort((a, b) => {
    if (a.publishedAt && b.publishedAt) return b.publishedAt.localeCompare(a.publishedAt) || a.slug.localeCompare(b.slug);
    if (a.publishedAt) return -1;
    if (b.publishedAt) return 1;
    return a.sortOrder - b.sortOrder || a.slug.localeCompare(b.slug);
  });
}

function replaceMarkers(source, replacement, filename) {
  const start = source.indexOf(startMarker);
  const end = source.indexOf(endMarker);
  if (start === -1 || end === -1 || start > end || source.indexOf(startMarker, start + 1) !== -1 || source.indexOf(endMarker, end + 1) !== -1) {
    throw new Error(`${filename}: CMS News markers must occur exactly once.`);
  }
  return `${source.slice(0, start)}${replacement}${source.slice(end + endMarker.length)}`;
}

function topList(articles) {
  const items = articles.slice(0, 3).map((article) => `          <li><a class="v2-news__item" href="./news/${article.slug}.html"><span class="v2-news__category">${escapeHtml(article.category)}</span><span class="v2-news__title">${escapeHtml(article.title)}</span><span aria-hidden="true">→</span></a></li>`);
  return `${startMarker}\n        <ul class="v2-news__list" data-cms-collection="news">\n${items.join('\n')}\n        </ul>\n        ${endMarker}`;
}

function archiveList(articles) {
  const items = articles.map((article) => `            <li><a href="./${article.slug}.html"><span class="news-archive__category">${escapeHtml(article.category)}</span><span>${escapeHtml(article.title)}</span><span aria-hidden="true">→</span></a></li>`);
  return `${startMarker}\n          <ul class="news-archive__list">\n${items.join('\n')}\n          </ul>\n          ${endMarker}`;
}

function descriptionFromBody(body) {
  return markdown.render(body).replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 120);
}

function articleHtml(template, article) {
  const replacements = {
    title: escapeHtml(article.title),
    category: escapeHtml(article.category),
    description: escapeHtml(descriptionFromBody(article.body) || article.title),
    publishedAt: article.publishedAt ? `<time class="news-detail__date" datetime="${article.publishedAt}">${article.publishedAt.replaceAll('-', '.')}</time>` : '',
    body: markdown.render(article.body).trim()
  };
  for (const key of Object.keys(replacements)) {
    if (!template.includes(`{{${key}}}`)) throw new Error(`Article template is missing {{${key}}}.`);
  }
  return template.replace(/{{(title|category|description|publishedAt|body)}}/g, (_, key) => replacements[key]);
}

async function copyStaticFiles() {
  for (const source of copiedPaths) {
    await fs.cp(path.join(root, source), path.join(outputDirectory, source), { recursive: true });
  }
  await fs.mkdir(path.join(outputDirectory, 'news'), { recursive: true });
}

async function build() {
  const [articles, articleTemplate] = await Promise.all([
    readArticles(),
    fs.readFile(path.join(root, 'templates', 'news-article.html'), 'utf8')
  ]);
  await fs.rm(outputDirectory, { recursive: true, force: true });
  await fs.mkdir(outputDirectory, { recursive: true });
  await copyStaticFiles();
  const [homeTemplate, archiveTemplate] = await Promise.all([
    fs.readFile(path.join(outputDirectory, 'index.html'), 'utf8'),
    fs.readFile(path.join(root, 'news', 'index.html'), 'utf8')
  ]);
  await Promise.all([
    fs.writeFile(path.join(outputDirectory, 'index.html'), replaceMarkers(homeTemplate, topList(articles), 'index.html')),
    fs.writeFile(path.join(outputDirectory, 'news', 'index.html'), replaceMarkers(archiveTemplate, archiveList(articles), 'news/index.html')),
    ...articles.map((article) => fs.writeFile(path.join(outputDirectory, article.outputPath), articleHtml(articleTemplate, article)))
  ]);
  console.log(`Built ${articles.length} news articles in dist/.`);
}

build().catch((error) => {
  console.error(`News build failed: ${error.message}`);
  process.exitCode = 1;
});

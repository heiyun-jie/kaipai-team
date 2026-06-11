import fs from 'node:fs';
import path from 'node:path';

const root = process.argv[2];
if (!root) {
  throw new Error('Usage: node verify-photo-unlimited.mjs <repo-root>');
}

const repoRoot = path.resolve(root);
const frontendRoot = path.join(repoRoot, 'kaipai-frontend');

const files = {
  edit: path.join(frontendRoot, 'src', 'pages', 'actor-profile', 'edit.vue'),
  section: path.join(frontendRoot, 'src', 'pages', 'actor-profile', 'components', 'PhotoCategorySection.vue'),
  enhance: path.join(frontendRoot, 'src', 'pages', 'actor-profile', 'profile-enhance.ts'),
  aiProfileCard: path.join(frontendRoot, 'src', 'pkg-card', 'ai-profile-card', 'index.vue'),
  cardList: path.join(frontendRoot, 'src', 'pkg-card', 'card-list', 'index.vue'),
  portfolio: path.join(frontendRoot, 'src', 'pkg-card', 'portfolio', 'index.vue'),
};

function read(filePath) {
  return fs.readFileSync(filePath, 'utf8');
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function assertNotIncludes(source, value, label) {
  assert(!source.includes(value), `${label} must not include: ${value}`);
}

function assertIncludes(source, value, label) {
  assert(source.includes(value), `${label} missing: ${value}`);
}

const edit = read(files.edit);
const section = read(files.section);
const enhance = read(files.enhance);
const aiProfileCard = read(files.aiProfileCard);
const cardList = read(files.cardList);
const portfolio = read(files.portfolio);

assertNotIncludes(section, '已上传 ${totalPhotos}/9', 'PhotoCategorySection total counter');
assertNotIncludes(section, '${categories[item.key].length}/3', 'PhotoCategorySection category counter');
assertNotIncludes(section, 'categories[item.key].length < 3', 'PhotoCategorySection add gate');
assertIncludes(section, '已上传 ${totalPhotos} 张', 'PhotoCategorySection unlimited total counter');
assertIncludes(section, '${categories[item.key].length} 张', 'PhotoCategorySection unlimited category counter');
assertIncludes(section, 'class="photo-category__add"', 'PhotoCategorySection add entry remains visible');

assertNotIncludes(edit, 'form.photoCategories[category].length >= 3', 'actor profile edit upload guard');
assertNotIncludes(edit, 'chooseImageFiles(3 - form.photoCategories[category].length)', 'actor profile edit remaining-count picker');
assertNotIncludes(edit, 'if (form.photoCategories[category].length >= 3) break', 'actor profile edit upload loop break');
assertNotIncludes(edit, '${form.photos.length}/9', 'actor profile edit photo stat');
assertIncludes(edit, "${form.photos.length} 张", 'actor profile edit photo stat unlimited label');
assertIncludes(edit, 'const filePaths = await chooseImageFiles(9)', 'actor profile edit batch picker remains per-action only');

assertNotIncludes(enhance, 'photoCategories.portrait || [])].slice(0, 3)', 'profile enhance portrait truncation');
assertNotIncludes(enhance, 'photoCategories.lifestyle || [])].slice(0, 3)', 'profile enhance lifestyle truncation');
assertNotIncludes(enhance, 'photoCategories.production || [])].slice(0, 3)', 'profile enhance production truncation');
assertNotIncludes(enhance, 'profile?.photos || [])].slice(0, 9)', 'profile enhance flat photo truncation');
assertIncludes(enhance, 'production: flatPhotos.slice(6)', 'profile enhance legacy flat overflow preservation');

assertNotIncludes(aiProfileCard, 'filter(Boolean).slice(0, 9)', 'AI profile card merged photo truncation');
assertNotIncludes(aiProfileCard, 'filter(Boolean).slice(0, 3)', 'AI profile card category truncation');
assertNotIncludes(aiProfileCard, 'nextCategories[targetKey].length < 3', 'AI profile card first-non-full gate');
assertNotIncludes(aiProfileCard, '].slice(0, 3)', 'AI profile card analysis image truncation');
assertIncludes(aiProfileCard, 'nextCategories.portrait = [normalizedUrl, ...nextCategories.portrait]', 'AI profile card analysis image prepends without cap');

assertNotIncludes(cardList, 'filter(Boolean).slice(0, 9)', 'card list merged photo truncation');
assertNotIncludes(cardList, 'filter(Boolean).slice(0, 3)', 'card list category truncation');
assertNotIncludes(cardList, 'const remaining = 9 - mergePhotoCategories(currentCategories).length', 'card list total remaining gate');
assertNotIncludes(cardList, '最多上传 9 张作品照片', 'card list max 9 toast');
assertNotIncludes(cardList, 'nextCategories[key].length < 3', 'card list first-non-full category gate');
assertIncludes(cardList, 'MAX_SELECTED_WORK_PHOTOS = 3', 'card list selected representative photo limit must remain');

assertNotIncludes(portfolio, '${allPhotos.length}/9', 'portfolio total counter');
assertNotIncludes(portfolio, '${photoCategories[category.key].length}/3', 'portfolio category counter');
assertIncludes(portfolio, '${allPhotos.length} 张', 'portfolio total counter unlimited label');
assertIncludes(portfolio, '${photoCategories[category.key].length} 张', 'portfolio category counter unlimited label');

console.log('Photo unlimited verification passed.');

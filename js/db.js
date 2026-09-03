/* ========================================
   خدمة البيانات - موقع الكوميكس
   إدارة البيانات باستخدام Firebase
   ======================================== */

// ---------- إعداد Firebase ----------
const firebaseConfig = {
  apiKey: "AIzaSyCpJiHhsyLQ8Dngj9gq8jbgDrwqxx41qzc",
  authDomain: "comicx-arabic.firebaseapp.com",
  databaseURL: "https://comicx-arabic-default-rtdb.firebaseio.com",
  projectId: "comicx-arabic",
  storageBucket: "comicx-arabic.firebasestorage.app",
  messagingSenderId: "199234060570",
  appId: "1:199234060570:web:9a328a93dec1ad34a2eca3"
};

// تهيئة Firebase
const app = firebase.initializeApp(firebaseConfig);
const db = firebase.database();

const DB = {
  // ---------- تهيئة قاعدة البيانات ----------
  async init() {
    // إنشاء التصنيفات الافتراضية إذا لم تكن موجودة
    const categoriesSnap = await db.ref('categories').once('value');
    if (!categoriesSnap.exists()) {
      await db.ref('categories').set([
        { id: 1, name: 'أكشن', slug: 'action' },
        { id: 2, name: 'مغامرة', slug: 'adventure' },
        { id: 3, name: 'خيال علمي', slug: 'sci-fi' },
        { id: 4, name: 'رعب', slug: 'horror' },
        { id: 5, name: 'كوميدي', slug: 'comedy' },
        { id: 6, name: 'رومانسي', slug: 'romance' },
        { id: 7, name: 'دراما', slug: 'drama' },
        { id: 8, name: 'رياضة', slug: 'sports' },
        { id: 9, name: 'تاريخي', slug: 'historical' },
        { id: 10, name: 'أخرى', slug: 'other' }
      ]);
    }

    // بيانات الأدمن الافتراضية
    const adminSnap = await db.ref('admin').once('value');
    if (!adminSnap.exists()) {
      await db.ref('admin').set({
        username: 'admin',
        password: btoa('admin123')
      });
    }

    // إعدادات الافتراضية
    const settingsSnap = await db.ref('settings').once('value');
    if (!settingsSnap.exists()) {
      await db.ref('settings').set({
        siteName: 'كوميكس عربية',
        siteDescription: 'أكبر مكتبة كوميكس عربية',
        theme: 'dark',
        itemsPerPage: 20
      });
    }

    // إنشاء مصفوفات فارغة إذا لم تكن موجودة
    const comicsSnap = await db.ref('comics').once('value');
    if (!comicsSnap.exists()) {
      await db.ref('comics').set([]);
    }

    const chaptersSnap = await db.ref('chapters').once('value');
    if (!chaptersSnap.exists()) {
      await db.ref('chapters').set([]);
    }
  },

  // ---------- عمليات القراءة ----------
  async getData(path) {
    const snapshot = await db.ref(path).once('value');
    return snapshot.val();
  },

  async setData(path, data) {
    await db.ref(path).set(data);
  },

  async updateData(path, data) {
    await db.ref(path).update(data);
  },

  async removeData(path) {
    await db.ref(path).remove();
  },

  // ---------- إدارة الكوميكس ----------
  async getComics() {
    const data = await this.getData('comics');
    return data ? Object.values(data) : [];
  },

  async getComic(id) {
    const snapshot = await db.ref('comics/' + id).once('value');
    return snapshot.val();
  },

  async addComic(comic) {
    const comics = await this.getComics();
    comic.id = Date.now();
    comic.createdAt = new Date().toISOString();
    comic.views = 0;
    comic.rating = 0;
    comic.ratingCount = 0;
    comics.unshift(comic);
    await this.setData('comics', comics);
    return comic;
  },

  async updateComic(id, updates) {
    const comics = await this.getComics();
    const index = comics.findIndex(c => c.id === id);
    if (index !== -1) {
      comics[index] = { ...comics[index], ...updates };
      await this.setData('comics', comics);
      return comics[index];
    }
    return null;
  },

  async deleteComic(id) {
    const comics = await this.getComics();
    await this.setData('comics', comics.filter(c => c.id !== id));
    // حذف الفصول المرتبطة
    const chapters = await this.getChapters();
    await this.setData('chapters', chapters.filter(ch => ch.comicId !== id));
  },

  // ---------- إدارة الفصول ----------
  async getChapters(comicId) {
    const data = await this.getData('chapters');
    let chapters = data ? Object.values(data) : [];
    if (comicId) {
      chapters = chapters.filter(ch => ch.comicId === comicId);
      chapters.sort((a, b) => a.number - b.number);
    }
    return chapters;
  },

  async getChapter(comicId, chapterNumber) {
    const chapters = await this.getChapters(comicId);
    return chapters.find(ch => ch.number === chapterNumber);
  },

  async addChapter(chapter) {
    const chapters = await this.getData('chapters') || [];
    chapter.id = Date.now();
    chapter.createdAt = new Date().toISOString();
    chapters.push(chapter);
    await this.setData('chapters', chapters);
    return chapter;
  },

  async updateChapter(id, updates) {
    const chapters = await this.getData('chapters') || [];
    const index = chapters.findIndex(ch => ch.id === id);
    if (index !== -1) {
      chapters[index] = { ...chapters[index], ...updates };
      await this.setData('chapters', chapters);
      return chapters[index];
    }
    return null;
  },

  async deleteChapter(id) {
    const chapters = await this.getData('chapters') || [];
    await this.setData('chapters', chapters.filter(ch => ch.id !== id));
  },

  // ---------- إدارة التصنيفات ----------
  async getCategories() {
    const data = await this.getData('categories');
    return data ? (Array.isArray(data) ? data : Object.values(data)) : [];
  },

  async addCategory(category) {
    const categories = await this.getCategories();
    category.id = Date.now();
    categories.push(category);
    await this.setData('categories', categories);
    return category;
  },

  async deleteCategory(id) {
    const categories = await this.getCategories();
    await this.setData('categories', categories.filter(c => c.id !== id));
  },

  // ---------- البحث والفلترة ----------
  async searchComics(query) {
    const comics = await this.getComics();
    const q = query.toLowerCase();
    return comics.filter(c =>
      c.title.toLowerCase().includes(q) ||
      c.description.toLowerCase().includes(q) ||
      c.category.toLowerCase().includes(q)
    );
  },

  async getComicsByCategory(category) {
    const comics = await this.getComics();
    return comics.filter(c => c.category === category);
  },

  async getLatestComics(limit = 20) {
    const comics = await this.getComics();
    return comics
      .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
      .slice(0, limit);
  },

  async getMostViewedComics(limit = 20) {
    const comics = await this.getComics();
    return comics
      .sort((a, b) => (b.views || 0) - (a.views || 0))
      .slice(0, limit);
  },

  // ---------- المشاهدات ----------
  async incrementViews(comicId) {
    const comic = await this.getComic(comicId);
    if (comic) {
      await this.updateComic(comicId, { views: (comic.views || 0) + 1 });
    }
  },

  // ---------- التقييم ----------
  async rateComic(comicId, rating) {
    const comic = await this.getComic(comicId);
    if (!comic) return;

    const totalRating = (comic.rating || 0) * (comic.ratingCount || 0) + rating;
    const newCount = (comic.ratingCount || 0) + 1;
    await this.updateComic(comicId, {
      rating: totalRating / newCount,
      ratingCount: newCount
    });
  },

  // ---------- الإحصائيات ----------
  async getStats() {
    const comics = await this.getComics();
    const chapters = await this.getData('chapters') || [];
    const chaptersList = Array.isArray(chapters) ? chapters : Object.values(chapters);
    const totalViews = comics.reduce((sum, c) => sum + (c.views || 0), 0);
    return {
      totalComics: comics.length,
      totalChapters: chaptersList.length,
      totalViews: totalViews,
      publishedComics: comics.filter(c => c.status === 'published').length,
      draftComics: comics.filter(c => c.status === 'draft').length
    };
  },

  // ---------- الإعدادات ----------
  async getSettings() {
    const data = await this.getData('settings');
    return data || { siteName: 'كوميكس عربية', theme: 'dark', itemsPerPage: 20 };
  },

  async saveSettings(settings) {
    await this.setData('settings', settings);
  },

  // ---------- تسجيل الدخول ----------
  async login(username, password) {
    const admin = await this.getData('admin');
    if (admin && admin.username === username && admin.password === btoa(password)) {
      sessionStorage.setItem('comicx_admin_auth', 'true');
      return true;
    }
    return false;
  },

  isAdmin() {
    return sessionStorage.getItem('comicx_admin_auth') === 'true';
  },

  logout() {
    sessionStorage.removeItem('comicx_admin_auth');
  },

  async changePassword(currentPass, newPass) {
    const admin = await this.getData('admin');
    if (admin.password !== btoa(currentPass)) {
      return { success: false, message: 'كلمة المرور الحالية غير صحيحة' };
    }
    await this.updateData('admin', { password: btoa(newPass) });
    return { success: true, message: 'تم تغيير كلمة المرور بنجاح' };
  }
};

/* ========================================
   خدمة البيانات - موقع الكوميكس
   إدارة البيانات باستخدام Firebase
   ======================================== */

// ---------- إعداد Firebase ----------
const firebaseConfig = {
  apiKey: "AIzaSyCpJiHhsyLQ8Dngj9gq8jbgDrwqxx41qzc",
  authDomain: "comicx-arabic.firebaseapp.com",
  databaseURL: "https://comicx-arabic-default-rtdb.europe-west1.firebasedatabase.app",
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
    try {
      // التحقق من وجود التصنيفات
      const catSnap = await db.ref('categories').once('value');
      if (!catSnap.exists()) {
        await db.ref('categories').set({
          cat_1: { id: 1, name: 'أكشن', slug: 'action' },
          cat_2: { id: 2, name: 'مغامرة', slug: 'adventure' },
          cat_3: { id: 3, name: 'خيال علمي', slug: 'sci-fi' },
          cat_4: { id: 4, name: 'رعب', slug: 'horror' },
          cat_5: { id: 5, name: 'كوميدي', slug: 'comedy' },
          cat_6: { id: 6, name: 'رومانسي', slug: 'romance' },
          cat_7: { id: 7, name: 'دراما', slug: 'drama' },
          cat_8: { id: 8, name: 'رياضة', slug: 'sports' },
          cat_9: { id: 9, name: 'تاريخي', slug: 'historical' },
          cat_10: { id: 10, name: 'أخرى', slug: 'other' }
        });
      }

      // التحقق من وجود الأدمن
      const adminSnap = await db.ref('admin').once('value');
      if (!adminSnap.exists()) {
        await db.ref('admin').set({
          username: 'admin',
          password: btoa('admin123')
        });
      }

      // التحقق من وجود الإعدادات
      const settingsSnap = await db.ref('settings').once('value');
      if (!settingsSnap.exists()) {
        await db.ref('settings').set({
          siteName: 'كوميكس عربية',
          siteDescription: 'أكبر مكتبة كوميكس عربية',
          theme: 'dark',
          itemsPerPage: 20
        });
      }
    } catch (error) {
      console.error('خطأ في التهيئة:', error);
    }
  },

  // ---------- عمليات القراءة ----------
  async getData(path) {
    const snapshot = await db.ref(path).once('value');
    return snapshot.val();
  },

  // ---------- إدارة الكوميكس ----------
  async getComics() {
    const data = await this.getData('comics');
    if (!data) return [];
    if (Array.isArray(data)) return data;
    return Object.values(data);
  },

  async getComic(id) {
    const comics = await this.getComics();
    return comics.find(c => c.id === id || c.id === parseInt(id));
  },

  async addComic(comic) {
    const newRef = db.ref('comics').push();
    comic.id = Date.now();
    comic.fbKey = newRef.key;
    comic.createdAt = new Date().toISOString();
    comic.views = 0;
    comic.rating = 0;
    comic.ratingCount = 0;
    await newRef.set(comic);
    return comic;
  },

  async updateComic(id, updates) {
    const comics = await this.getComics();
    const comic = comics.find(c => c.id === id || c.id === parseInt(id));
    if (comic && comic.fbKey) {
      await db.ref('comics/' + comic.fbKey).update(updates);
      return { ...comic, ...updates };
    }
    return null;
  },

  async deleteComic(id) {
    const comics = await this.getComics();
    const comic = comics.find(c => c.id === id || c.id === parseInt(id));
    if (comic && comic.fbKey) {
      await db.ref('comics/' + comic.fbKey).remove();
    }
    // حذف الفصول المرتبطة
    const chaptersSnap = await db.ref('chapters').once('value');
    const chaptersData = chaptersSnap.val();
    if (chaptersData) {
      Object.entries(chaptersData).forEach(async ([key, ch]) => {
        if (ch.comicId === id || ch.comicId === parseInt(id)) {
          await db.ref('chapters/' + key).remove();
        }
      });
    }
  },

  // ---------- إدارة الفصول ----------
  async getChapters(comicId) {
    const data = await this.getData('chapters');
    if (!data) return [];
    let chapters = Array.isArray(data) ? data : Object.values(data);
    if (comicId) {
      chapters = chapters.filter(ch => ch.comicId === comicId || ch.comicId === parseInt(comicId));
      chapters.sort((a, b) => a.number - b.number);
    }
    return chapters;
  },

  async addChapter(chapter) {
    const newRef = db.ref('chapters').push();
    chapter.id = Date.now();
    chapter.fbKey = newRef.key;
    chapter.createdAt = new Date().toISOString();
    await newRef.set(chapter);
    return chapter;
  },

  async updateChapter(id, updates) {
    const data = await this.getData('chapters');
    if (!data) return null;
    const entries = Object.entries(data);
    for (const [key, ch] of entries) {
      if (ch.id === id || ch.id === parseInt(id)) {
        await db.ref('chapters/' + key).update(updates);
        return { ...ch, ...updates };
      }
    }
    return null;
  },

  async deleteChapter(id) {
    const data = await this.getData('chapters');
    if (!data) return;
    const entries = Object.entries(data);
    for (const [key, ch] of entries) {
      if (ch.id === id || ch.id === parseInt(id)) {
        await db.ref('chapters/' + key).remove();
      }
    }
  },

  // ---------- إدارة التصنيفات ----------
  async getCategories() {
    const data = await this.getData('categories');
    if (!data) return [];
    if (Array.isArray(data)) return data;
    return Object.values(data);
  },

  async addCategory(category) {
    const newRef = db.ref('categories').push();
    category.id = Date.now();
    category.fbKey = newRef.key;
    await newRef.set(category);
    return category;
  },

  async deleteCategory(id) {
    const data = await this.getData('categories');
    if (!data) return;
    const entries = Object.entries(data);
    for (const [key, cat] of entries) {
      if (cat.id === id || cat.id === parseInt(id)) {
        await db.ref('categories/' + key).remove();
      }
    }
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
    if (comic && comic.fbKey) {
      await db.ref('comics/' + comic.fbKey + '/views').set((comic.views || 0) + 1);
    }
  },

  // ---------- التقييم ----------
  async rateComic(comicId, rating) {
    const comic = await this.getComic(comicId);
    if (!comic || !comic.fbKey) return;
    const totalRating = (comic.rating || 0) * (comic.ratingCount || 0) + rating;
    const newCount = (comic.ratingCount || 0) + 1;
    await db.ref('comics/' + comic.fbKey).update({
      rating: totalRating / newCount,
      ratingCount: newCount
    });
  },

  // ---------- الإحصائيات ----------
  async getStats() {
    const comics = await this.getComics();
    const chapters = await this.getChapters();
    const totalViews = comics.reduce((sum, c) => sum + (c.views || 0), 0);
    return {
      totalComics: comics.length,
      totalChapters: chapters.length,
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
    await db.ref('settings').set(settings);
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
    await db.ref('admin/password').set(btoa(newPass));
    return { success: true, message: 'تم تغيير كلمة المرور بنجاح' };
  }
};

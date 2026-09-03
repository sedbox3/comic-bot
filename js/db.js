/* ========================================
   خدمة البيانات - موقع الكوميكس
   إدارة البيانات باستخدام localStorage
   ======================================== */

const DB = {
  // ---------- المفتاح الأساسي للتخزين ----------
  KEYS: {
    COMICS: 'comicx_comics',
    CHAPTERS: 'comicx_chapters',
    CATEGORIES: 'comicx_categories',
    SETTINGS: 'comicx_settings',
    ADMIN: 'comicx_admin',
    RATINGS: 'comicx_ratings',
    VIEWS: 'comicx_views',
    READING_POS: 'comicx_reading_pos'
  },

  // ---------- تهيئة قاعدة البيانات ----------
  init() {
    // إنشاء بيانات افتراضية إذا لم تكن موجودة
    if (!localStorage.getItem(this.KEYS.CATEGORIES)) {
      this.save(this.KEYS.CATEGORIES, [
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
    if (!localStorage.getItem(this.KEYS.ADMIN)) {
      this.save(this.KEYS.ADMIN, {
        username: 'admin',
        // كلمة المرور: admin123 مشفرة بـ btoa
        password: btoa('admin123')
      });
    }

    // إعدادات الافتراضية
    if (!localStorage.getItem(this.KEYS.SETTINGS)) {
      this.save(this.KEYS.SETTINGS, {
        siteName: 'كوميكس عربية',
        siteDescription: 'أكبر مكتبة كوميكس عربية',
        theme: 'dark',
        itemsPerPage: 20
      });
    }

    // إنشاء مصفوفات فارغة إذا لم تكن موجودة
    if (!localStorage.getItem(this.KEYS.COMICS)) {
      this.save(this.KEYS.COMICS, []);
    }

    if (!localStorage.getItem(this.KEYS.CHAPTERS)) {
      this.save(this.KEYS.CHAPTERS, []);
    }
  },

  // ----------عمليات CRUD الأساسية ----------
  save(key, data) {
    localStorage.setItem(key, JSON.stringify(data));
  },

  load(key) {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : null;
  },

  remove(key) {
    localStorage.removeItem(key);
  },

  // ---------- إدارة الكوميكس ----------
  getComics() {
    return this.load(this.KEYS.COMICS) || [];
  },

  getComic(id) {
    const comics = this.getComics();
    return comics.find(c => c.id === id);
  },

  addComic(comic) {
    const comics = this.getComics();
    comic.id = Date.now();
    comic.createdAt = new Date().toISOString();
    comic.views = 0;
    comic.rating = 0;
    comic.ratingCount = 0;
    comics.unshift(comic);
    this.save(this.KEYS.COMICS, comics);
    return comic;
  },

  updateComic(id, updates) {
    const comics = this.getComics();
    const index = comics.findIndex(c => c.id === id);
    if (index !== -1) {
      comics[index] = { ...comics[index], ...updates };
      this.save(this.KEYS.COMICS, comics);
      return comics[index];
    }
    return null;
  },

  deleteComic(id) {
    const comics = this.getComics();
    this.save(this.KEYS.COMICS, comics.filter(c => c.id !== id));
    // حذف الفصول المرتبطة
    const chapters = this.getChapters();
    this.save(this.KEYS.CHAPTERS, chapters.filter(ch => ch.comicId !== id));
  },

  // ---------- إدارة الفصول ----------
  getChapters(comicId) {
    const chapters = this.load(this.KEYS.CHAPTERS) || [];
    if (comicId) {
      return chapters.filter(ch => ch.comicId === comicId).sort((a, b) => a.number - b.number);
    }
    return chapters;
  },

  getChapter(comicId, chapterNumber) {
    const chapters = this.getChapters(comicId);
    return chapters.find(ch => ch.number === chapterNumber);
  },

  addChapter(chapter) {
    const chapters = this.load(this.KEYS.CHAPTERS) || [];
    chapter.id = Date.now();
    chapter.createdAt = new Date().toISOString();
    chapters.push(chapter);
    this.save(this.KEYS.CHAPTERS, chapters);
    return chapter;
  },

  updateChapter(id, updates) {
    const chapters = this.load(this.KEYS.CHAPTERS) || [];
    const index = chapters.findIndex(ch => ch.id === id);
    if (index !== -1) {
      chapters[index] = { ...chapters[index], ...updates };
      this.save(this.KEYS.CHAPTERS, chapters);
      return chapters[index];
    }
    return null;
  },

  deleteChapter(id) {
    const chapters = this.load(this.KEYS.CHAPTERS) || [];
    this.save(this.KEYS.CHAPTERS, chapters.filter(ch => ch.id !== id));
  },

  // ---------- إدارة التصنيفات ----------
  getCategories() {
    return this.load(this.KEYS.CATEGORIES) || [];
  },

  addCategory(category) {
    const categories = this.getCategories();
    category.id = Date.now();
    categories.push(category);
    this.save(this.KEYS.CATEGORIES, categories);
    return category;
  },

  deleteCategory(id) {
    const categories = this.getCategories();
    this.save(this.KEYS.CATEGORIES, categories.filter(c => c.id !== id));
  },

  // ---------- البحث والفلترة ----------
  searchComics(query) {
    const comics = this.getComics();
    const q = query.toLowerCase();
    return comics.filter(c =>
      c.title.toLowerCase().includes(q) ||
      c.description.toLowerCase().includes(q) ||
      c.category.toLowerCase().includes(q)
    );
  },

  getComicsByCategory(category) {
    return this.getComics().filter(c => c.category === category);
  },

  getLatestComics(limit = 20) {
    return this.getComics()
      .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
      .slice(0, limit);
  },

  getMostViewedComics(limit = 20) {
    return this.getComics()
      .sort((a, b) => b.views - a.views)
      .slice(0, limit);
  },

  // ---------- المشاهدات ----------
  incrementViews(comicId) {
    const views = this.load(this.KEYS.VIEWS) || {};
    views[comicId] = (views[comicId] || 0) + 1;
    this.save(this.KEYS.VIEWS, views);
    // تحديث عداد المشاهدات في الكوميكس
    const comic = this.getComic(comicId);
    if (comic) {
      this.updateComic(comicId, { views: views[comicId] });
    }
  },

  getViews(comicId) {
    const views = this.load(this.KEYS.VIEWS) || {};
    return views[comicId] || 0;
  },

  // ---------- التقييم ----------
  rateComic(comicId, rating) {
    const ratings = this.load(this.KEYS.RATINGS) || {};
    const comic = this.getComic(comicId);
    if (!comic) return;

    const oldRating = ratings[comicId] || 0;
    ratings[comicId] = rating;
    this.save(this.KEYS.RATINGS, ratings);

    // حساب متوسط التقييم
    const totalRating = (comic.rating * comic.ratingCount) - oldRating + rating;
    const newCount = oldRating === 0 ? comic.ratingCount + 1 : comic.ratingCount;
    this.updateComic(comicId, {
      rating: totalRating / newCount,
      ratingCount: newCount
    });
  },

  getUserRating(comicId) {
    const ratings = this.load(this.KEYS.RATINGS) || {};
    return ratings[comicId] || 0;
  },

  // ---------- موضع القراءة ----------
  saveReadingPosition(comicId, chapterNumber, page) {
    const positions = this.load(this.KEYS.READING_POS) || {};
    positions[`${comicId}_${chapterNumber}`] = page;
    this.save(this.KEYS.READING_POS, positions);
  },

  getReadingPosition(comicId, chapterNumber) {
    const positions = this.load(this.KEYS.READING_POS) || {};
    return positions[`${comicId}_${chapterNumber}`] || 0;
  },

  // ---------- تسجيل الدخول ----------
  login(username, password) {
    const admin = this.load(this.KEYS.ADMIN);
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

  // ---------- الإحصائيات ----------
  getStats() {
    const comics = this.getComics();
    const chapters = this.getChapters();
    const totalViews = comics.reduce((sum, c) => sum + (c.views || 0), 0);
    return {
      totalComics: comics.length,
      totalChapters: chapters.length,
      totalViews: totalViews,
      publishedComics: comics.filter(c => c.status === 'published').length,
      draftComics: comics.filter(c => c.status === 'draft').length
    };
  },

};

// تهيئة قاعدة البيانات عند التحميل
DB.init();

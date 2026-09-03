/* ========================================
   واجهة المستخدم المشتركة - موقع الكوميكس
   ======================================== */

const UI = {
  // ---------- إنشاء شريط التنقل ----------
  renderNavbar(activePage = '') {
    const settings = DB.load(DB.KEYS.SETTINGS) || {};
    const theme = settings.theme || 'dark';

    return `
    <nav class="navbar">
      <a href="index.html" class="navbar-brand">
        <svg viewBox="0 0 24 24" fill="currentColor" style="color: var(--accent);">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
        </svg>
        ${settings.siteName || 'كوميكس عربية'}
      </a>
      
      <div class="navbar-links" id="navLinks">
        <a href="index.html" class="${activePage === 'home' ? 'active' : ''}">الرئيسية</a>
        <a href="browse.html" class="${activePage === 'browse' ? 'active' : ''}">تصفح</a>
        <a href="browse.html?filter=popular" class="${activePage === 'popular' ? 'active' : ''}">الأكثر قراءة</a>
        <a href="browse.html?filter=latest" class="${activePage === 'latest' ? 'active' : ''}">أحدث الإضافات</a>
      </div>
      
      <div class="navbar-actions">
        <div class="search-box">
          <input type="text" id="searchInput" placeholder="ابحث عن كوميكس..." 
                 onkeypress="if(event.key==='Enter') UI.doSearch(this.value)">
          <span class="search-icon"><i class="fas fa-search"></i></span>
        </div>
        
        <button class="theme-toggle" onclick="UI.toggleTheme()" title="تبديل الثيم">
          <i class="fas ${theme === 'dark' ? 'fa-sun' : 'fa-moon'}"></i>
        </button>
        
        <button class="mobile-menu-btn" onclick="UI.toggleMobileMenu()">
          <i class="fas fa-bars"></i>
        </button>
      </div>
    </nav>`;
  },

  // ---------- إنشاء الفوتر ----------
  renderFooter() {
    const categories = DB.getCategories().slice(0, 6);
    return `
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-section">
          <h3>كوميكس عربية</h3>
          <p style="color: var(--text-secondary); line-height: 1.8;">
            أكبر مكتبة كوميكس عربية مجانية. استمتع بآلاف القصص المصورة بجودة عالية.
          </p>
        </div>
        <div class="footer-section">
          <h3>روابط سريعة</h3>
          <a href="index.html">الرئيسية</a>
          <a href="browse.html">تصفح الكل</a>
          <a href="browse.html?filter=popular">الأكثر قراءة</a>
          <a href="browse.html?filter=latest">أحدث الإضافات</a>
        </div>
        <div class="footer-section">
          <h3>التصنيفات</h3>
          ${categories.map(c => `<a href="browse.html?category=${c.name}">${c.name}</a>`).join('')}
        </div>
        <div class="footer-section">
          <h3>تابعنا</h3>
          <a href="#"><i class="fab fa-twitter"></i> تويتر</a>
          <a href="#"><i class="fab fa-discord"></i> ديسكورد</a>
          <a href="#"><i class="fab fa-instagram"></i> انستغرام</a>
        </div>
      </div>
      <div class="footer-bottom">
        <p>© ${new Date().getFullYear()} كوميكس عربية. جميع الحقوق محفوظة.</p>
      </div>
    </footer>`;
  },

  // ---------- إنشاء بطاقة كوميكس ----------
  renderComicCard(comic) {
    const chapters = DB.getChapters(comic.id);
    return `
    <div class="comic-card fade-in" onclick="window.location.href='comic.html?id=${comic.id}'">
      <div class="cover">
        <img src="${comic.cover}" alt="${comic.title}" loading="lazy">
        ${comic.status === 'draft' ? '<span class="badge">مسودة</span>' : ''}
        ${chapters.length > 0 ? `<span class="badge" style="left:10px;right:auto;background:var(--accent2)">${chapters.length} فصل</span>` : ''}
      </div>
      <div class="card-info">
        <h3 class="card-title">${comic.title}</h3>
        <div class="card-meta">
          <span class="card-rating">
            <i class="fas fa-star"></i> ${comic.rating ? comic.rating.toFixed(1) : '0.0'}
          </span>
          <span class="card-views">
            <i class="fas fa-eye"></i> ${this.formatNumber(comic.views || 0)}
          </span>
        </div>
      </div>
    </div>`;
  },

  // ---------- إنشاء شبكة الكوميكس ----------
  renderComicsGrid(comics) {
    if (comics.length === 0) {
      return `
      <div class="empty-state">
        <div class="empty-icon"><i class="fas fa-book-open"></i></div>
        <h3>لا توجد نتائج</h3>
        <p>لم يتم العثور على كوميكس مطابقة.</p>
      </div>`;
    }
    return `
    <div class="comics-grid">
      ${comics.map(c => this.renderComicCard(c)).join('')}
    </div>`;
  },

  // ---------- إنشاء قائمة التصنيفات ----------
  renderCategoriesBar(selectedCategory = '') {
    const categories = DB.getCategories();
    return `
    <div class="categories-bar">
      <button class="category-chip ${!selectedCategory ? 'active' : ''}" 
              onclick="UI.filterByCategory('')">
        الكل
      </button>
      ${categories.map(c => `
        <button class="category-chip ${selectedCategory === c.name ? 'active' : ''}" 
                onclick="UI.filterByCategory('${c.name}')">
          ${c.name}
        </button>
      `).join('')}
    </div>`;
  },

  // ---------- إنشاء تقييم النجوم ----------
  renderStarRating(comicId, currentRating = 0) {
    const userRating = DB.getUserRating(comicId);
    return `
    <div class="star-rating" data-comic-id="${comicId}">
      ${[1, 2, 3, 4, 5].map(star => `
        <span class="star ${star <= (userRating || currentRating) ? 'filled' : ''}" 
              onclick="UI.rateComic(${comicId}, ${star})" 
              onmouseover="UI.previewRating(this, ${star})"
              onmouseout="UI.resetRatingPreview(this)">
          ★
        </span>
      `).join('')}
    </div>`;
  },

  // ---------- تقييم الكوميكس ----------
  rateComic(comicId, rating) {
    DB.rateComic(comicId, rating);
    this.showAlert('تم تسجيل تقييمك بنجاح!', 'success');
    // تحديث النجوم
    const container = document.querySelector(`.star-rating[data-comic-id="${comicId}"]`);
    if (container) {
      container.querySelectorAll('.star').forEach((star, i) => {
        star.classList.toggle('filled', i < rating);
      });
    }
  },

  previewRating(star, value) {
    const container = star.parentElement;
    container.querySelectorAll('.star').forEach((s, i) => {
      s.style.color = i < value ? 'var(--star)' : 'var(--border)';
    });
  },

  resetRatingPreview(star) {
    const container = star.parentElement;
    const comicId = container.dataset.comicId;
    const userRating = DB.getUserRating(parseInt(comicId));
    const comic = DB.getComic(parseInt(comicId));
    const currentRating = userRating || (comic ? comic.rating : 0);
    container.querySelectorAll('.star').forEach((s, i) => {
      s.style.color = '';
      s.classList.toggle('filled', i < currentRating);
    });
  },

  // ---------- عرض التنبيه ----------
  showAlert(message, type = 'success') {
    const existing = document.querySelector('.alert');
    if (existing) existing.remove();

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alert.style.position = 'fixed';
    alert.style.top = '80px';
    alert.style.left = '50%';
    alert.style.transform = 'translateX(-50%)';
    alert.style.zIndex = '9999';
    alert.style.minWidth = '300px';
    alert.style.textAlign = 'center';
    alert.style.animation = 'fadeIn 0.3s ease';

    document.body.appendChild(alert);
    setTimeout(() => alert.remove(), 3000);
  },

  // ---------- تبديل الثيم ----------
  toggleTheme() {
    const settings = DB.load(DB.KEYS.SETTINGS) || {};
    const newTheme = settings.theme === 'dark' ? 'light' : 'dark';
    settings.theme = newTheme;
    DB.save(DB.KEYS.SETTINGS, settings);
    document.documentElement.setAttribute('data-theme', newTheme);
    // تحديث أيقونة الزر
    const btn = document.querySelector('.theme-toggle');
    if (btn) {
      btn.innerHTML = `<i class="fas ${newTheme === 'dark' ? 'fa-sun' : 'fa-moon'}"></i>`;
    }
  },

  // ---------- تحميل الثيم ----------
  loadTheme() {
    const settings = DB.load(DB.KEYS.SETTINGS) || {};
    document.documentElement.setAttribute('data-theme', settings.theme || 'dark');
  },

  // ---------- قائمة الموبايل ----------
  toggleMobileMenu() {
    document.getElementById('navLinks').classList.toggle('show');
  },

  // ---------- البحث ----------
  doSearch(query) {
    if (query.trim()) {
      window.location.href = `browse.html?search=${encodeURIComponent(query.trim())}`;
    }
  },

  // ---------- فلترة التصنيف ----------
  filterByCategory(category) {
    const url = new URL(window.location);
    if (category) {
      url.searchParams.set('category', category);
    } else {
      url.searchParams.delete('category');
    }
    window.location = url;
  },

  // ---------- تنسيق الأرقام ----------
  formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  },

  // ---------- تحليل URL ----------
  getUrlParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
  },

  // ---------- شاشة التحميل ----------
  showLoader(container) {
    container.innerHTML = '<div class="loader"><div class="spinner"></div></div>';
  },

  // ---------- إنشاء التخطيط الكامل ----------
  renderPage(activePage, content) {
    return `
    ${this.renderNavbar(activePage)}
    <main class="main-content">
      ${content}
    </main>
    ${this.renderFooter()}`;
  }
};

// تحميل الثيم عند بدء التحميل
UI.loadTheme();

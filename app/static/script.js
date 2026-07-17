let token = '';
let currentImageUrl = '';
let currentCaption = '';
let currentFile = null;

document.addEventListener('DOMContentLoaded', () => {
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            navButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const tab = btn.dataset.tab;
            showTab(tab);
        });
    });

    if (localStorage.getItem('token')) {
        token = localStorage.getItem('token');
        document.getElementById('login-screen').classList.add('hidden');
        document.getElementById('main-screen').classList.remove('hidden');
        showTab('home');
    }
});

async function login() {
    const password = document.getElementById('password').value;
    const res = await fetch('/auth/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({password})
    });
    if (res.ok) {
        const data = await res.json();
        token = data.access_token;
        localStorage.setItem('token', token);
        document.getElementById('login-screen').classList.add('hidden');
        document.getElementById('main-screen').classList.remove('hidden');
        showTab('home');
    } else {
        document.getElementById('login-error').innerText = 'كلمة المرور غير صحيحة';
    }
}

function showTab(tab) {
    const container = document.getElementById('tab-content');
    switch(tab) {
        case 'home': renderHome(container); break;
        case 'upload': renderUpload(container); break;
        case 'schedule': renderSchedule(container); break;
        case 'analytics': renderAnalytics(container); break;
    }
}

function renderHome(container) {
    container.innerHTML = `
        <h2 class="gold-text">🏠 مرحباً بك</h2>
        <div class="cards-container">
            <div class="stat-card"><i class="fas fa-image"></i><div class="value" id="quick-posts">--</div><div class="label">منشورات اليوم</div></div>
            <div class="stat-card"><i class="fas fa-calendar-check"></i><div class="value" id="quick-scheduled">--</div><div class="label">مجدولة</div></div>
        </div>
        <button class="btn-gold" onclick="showTab('upload')" style="width:100%">📤 رفع منشور جديد</button>
    `;
}

function renderUpload(container) {
    container.innerHTML = `
        <h2 class="gold-text">📤 رفع منشور</h2>
        <input type="file" id="media-file" accept="image/*,video/*" onchange="previewMedia(this)">
        <div class="upload-preview" id="upload-preview">
            <i class="fas fa-cloud-upload-alt" style="font-size:48px;color:#7E8299;"></i>
        </div>
        <input type="text" id="idea-input" placeholder="الفكرة الأساسية">
        <input type="text" id="feeling-input" placeholder="الشعور أو الأجواء">
        <input type="text" id="hashtags-input" placeholder="هاشتاغات (اختياري)">
        <button onclick="generateAICaption()">🪄 توليد الكابشن</button>
        <div id="caption-area" class="caption-box hidden">
            <textarea id="generated-caption"></textarea>
        </div>
        <div class="schedule-options">
            <input type="datetime-local" id="scheduled-time" style="flex:1">
            <button onclick="publishNow()">🚀 نشر الآن</button>
            <button onclick="schedulePost()">📅 جدولة</button>
        </div>
        <div id="upload-status" class="error-text"></div>
    `;
}

function previewMedia(input) {
    const file = input.files[0];
    if (file) {
        currentFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            const previewDiv = document.getElementById('upload-preview');
            if (file.type.startsWith('image/')) {
                previewDiv.innerHTML = `<img src="${e.target.result}" alt="preview">`;
            } else if (file.type.startsWith('video/')) {
                previewDiv.innerHTML = `<video src="${e.target.result}" controls></video>`;
            }
        };
        reader.readAsDataURL(file);
    }
}

async function generateAICaption() {
    const idea = document.getElementById('idea-input').value;
    const feeling = document.getElementById('feeling-input').value;
    const hashtags = document.getElementById('hashtags-input').value;
    const statusDiv = document.getElementById('upload-status');

    if (!idea && !feeling) {
        statusDiv.innerText = 'أدخل الفكرة أو الشعور على الأقل';
        return;
    }
    if (!currentFile) {
        statusDiv.innerText = 'اختر ملفاً أولاً';
        return;
    }

    const bullets = `فكرة: ${idea}\nشعور: ${feeling}\nهاشتاغات: ${hashtags}`;
    const formData = new FormData();
    formData.append('file', currentFile);
    formData.append('bullets', bullets);

    try {
        statusDiv.innerText = '⏳ جاري التوليد...';
        const res = await fetch('/content/upload', {
            method: 'POST',
            headers: {'Authorization': `Bearer ${token}`},
            body: formData
        });
        const data = await res.json();
        if (res.ok) {
            currentImageUrl = data.image_url;
            currentCaption = data.suggested_caption;
            document.getElementById('caption-area').classList.remove('hidden');
            document.getElementById('generated-caption').value = currentCaption;
            statusDiv.innerText = '';
        } else {
            statusDiv.innerText = 'خطأ: ' + (data.detail || JSON.stringify(data));
        }
    } catch (err) {
        statusDiv.innerText = 'فشل الاتصال بالخادم: ' + err.message;
    }
}

async function publishNow() {
    const caption = document.getElementById('generated-caption').value;
    if (!currentImageUrl || !caption) return alert('تأكد من رفع الصورة وتوليد الكابشن');
    await submitPost(null, caption);
}

async function schedulePost() {
    const scheduledTime = document.getElementById('scheduled-time').value;
    if (!scheduledTime) return alert('اختر وقتاً للجدولة');
    const caption = document.getElementById('generated-caption').value;
    if (!currentImageUrl || !caption) return alert('تأكد من رفع الصورة وتوليد الكابشن');
    await submitPost(new Date(scheduledTime).toISOString(), caption);
}

async function submitPost(scheduledTime, caption) {
    const payload = {
        image_url: currentImageUrl,
        caption: caption,
        scheduled_time: scheduledTime
    };
    const res = await fetch('/content/approve', {
        method: 'POST',
        headers: {'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    const data = await res.json();
    document.getElementById('upload-status').innerText = data.message || 'تم';
    document.getElementById('caption-area').classList.add('hidden');
    document.getElementById('media-file').value = '';
    document.getElementById('upload-preview').innerHTML = '<i class="fas fa-cloud-upload-alt"></i>';
    currentImageUrl = '';
    currentCaption = '';
}

async function loadSchedule() {
    const res = await fetch('/schedule/', {headers: {'Authorization': `Bearer ${token}`}});
    const data = await res.json();
    const list = document.getElementById('schedule-list');
    if (list) {
        list.innerHTML = '';
        data.forEach(item => {
            const li = document.createElement('li');
            li.innerText = `${item.caption.substring(0,30)}... - ${new Date(item.scheduled_time).toLocaleString()}`;
            list.appendChild(li);
        });
    }
}

function renderSchedule(container) {
    container.innerHTML = `
        <h2 class="gold-text">📅 المنشورات المجدولة</h2>
        <ul id="schedule-list"></ul>
    `;
    loadSchedule();
}

async function refreshAnalytics() {
    await fetch('/analytics/refresh', {method: 'POST', headers: {'Authorization': `Bearer ${token}`}});
    loadAnalytics();
}

async function loadAnalytics() {
    const res = await fetch('/analytics/latest', {headers: {'Authorization': `Bearer ${token}`}});
    const data = await res.json();
    const div = document.getElementById('analytics-content');
    if (div) {
        if (data.detail) {
            div.innerText = data.detail;
        } else {
            div.innerHTML = `
                <div class="cards-container">
                    <div class="stat-card"><i class="fas fa-users"></i><div class="value">${data.followers}</div><div class="label">متابعين</div></div>
                    <div class="stat-card"><i class="fas fa-eye"></i><div class="value">${data.impressions}</div><div class="label">ظهور</div></div>
                    <div class="stat-card"><i class="fas fa-chart-line"></i><div class="value">${data.reach}</div><div class="label">وصول</div></div>
                    <div class="stat-card"><i class="fas fa-heart"></i><div class="value">${data.engagement}</div><div class="label">تفاعل</div></div>
                </div>
                <div class="caption-box"><h4>📝 التقرير الأسبوعي</h4><p>${data.report_text}</p></div>
            `;
        }
    }
}

function renderAnalytics(container) {
    container.innerHTML = `
        <h2 class="gold-text">📊 التحليلات</h2>
        <button class="btn-gold" onclick="refreshAnalytics()" style="margin-bottom:15px;">🔄 تحديث التقرير</button>
        <div id="analytics-content"></div>
    `;
    loadAnalytics();
}

/* ============ 小账本 · 核心逻辑 ============ */

// 预设分类
const CATEGORIES = {
  expense: [
    { key: 'meal',   emoji: '🍜', name: '餐饮' },
    { key: 'trans',  emoji: '🚗', name: '交通' },
    { key: 'shop',   emoji: '🛒', name: '购物' },
    { key: 'home',   emoji: '🏠', name: '居住' },
    { key: 'fun',    emoji: '🎮', name: '娱乐' },
    { key: 'health', emoji: '💊', name: '医疗' },
    { key: 'study',  emoji: '📚', name: '学习' },
    { key: 'gift',   emoji: '🎁', name: '人情' },
    { key: 'beauty', emoji: '💄', name: '美妆' },
    { key: 'pet',    emoji: '🐶', name: '宠物' },
    { key: 'travel', emoji: '✈️', name: '旅行' },
    { key: 'tech',   emoji: '📱', name: '数码' },
    { key: 'otherE', emoji: '📦', name: '其他' },
  ],
  income: [
    { key: 'salary', emoji: '💰', name: '工资' },
    { key: 'redpack',emoji: '🧧', name: '红包' },
    { key: 'invest', emoji: '📈', name: '理财' },
    { key: 'side',   emoji: '💼', name: '兼职' },
    { key: 'bonus',  emoji: '🏆', name: '奖金' },
    { key: 'otherI', emoji: '✨', name: '其他' },
  ]
};

// 存储 key
const STORAGE_KEY = 'ledger_bills_v1';

/* ============ 数据层 ============ */
const Store = {
  getAll() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch { return []; }
  },
  save(bills) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(bills));
  },
  add(bill) {
    const bills = this.getAll();
    bills.unshift(bill);
    this.save(bills);
  },
  update(id, patch) {
    const bills = this.getAll();
    const idx = bills.findIndex(b => b.id === id);
    if (idx !== -1) {
      bills[idx] = { ...bills[idx], ...patch };
      this.save(bills);
    }
  },
  remove(id) {
    const bills = this.getAll().filter(b => b.id !== id);
    this.save(bills);
  },
};

/* ============ 工具函数 ============ */
function pad(n) { return n < 10 ? '0' + n : '' + n; }
function fmtDate(d) {
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
}
function fmtCNDate(dateStr) {
  const [y, m, d] = dateStr.split('-');
  return `${y}年${parseInt(m)}月${parseInt(d)}日`;
}
function fmtAmount(n) {
  return Number(n).toFixed(2);
}
function weekDay(dateStr) {
  const days = ['周日','周一','周二','周三','周四','周五','周六'];
  return days[new Date(dateStr).getDay()];
}
function getCat(type, key) {
  return CATEGORIES[type].find(c => c.key === key) || { emoji: '📦', name: '其他' };
}
function isSameMonth(dateStr, y, m) {
  const [yy, mm] = dateStr.split('-');
  return parseInt(yy) === y && parseInt(mm) === m;
}
function genId() { return Date.now().toString(36) + Math.random().toString(36).slice(2,7); }

/* ============ 状态 ============ */
const now = new Date();
const state = {
  curYear: now.getFullYear(),
  curMonth: now.getMonth() + 1,
  currentType: 'expense',       // 弹窗中选中的类型
  editType: 'expense',          // 编辑弹窗的类型
  statsType: 'expense',         // 分类统计的类型
  selectedCategory: null,       // 弹窗中选中的分类 key
  editCategory: null,
};

/* ============ 渲染：顶部汇总 ============ */
function renderSummary() {
  const bills = Store.getAll().filter(b => isSameMonth(b.date, state.curYear, state.curMonth));
  let income = 0, expense = 0;
  bills.forEach(b => {
    if (b.type === 'income') income += b.amount;
    else expense += b.amount;
  });
  document.getElementById('monthLabel').textContent = `${state.curYear}年${state.curMonth}月`;
  document.getElementById('monthIncome').textContent = fmtAmount(income);
  document.getElementById('monthExpense').textContent = fmtAmount(expense);
  document.getElementById('monthBalance').textContent = fmtAmount(income - expense);
}

/* ============ 渲染：账单列表 ============ */
function renderBillList() {
  const bills = Store.getAll();
  // 过滤当前月份
  const filtered = bills.filter(b => isSameMonth(b.date, state.curYear, state.curMonth));

  const listEl = document.getElementById('billList');
  const emptyEl = document.getElementById('emptyTip');
  listEl.innerHTML = '';

  if (filtered.length === 0) {
    emptyEl.classList.remove('hidden');
    return;
  }
  emptyEl.classList.add('hidden');

  // 按日期分组（日期倒序）
  const groups = {};
  filtered.forEach(b => {
    (groups[b.date] = groups[b.date] || []).push(b);
  });
  const sortedDates = Object.keys(groups).sort((a, b) => b.localeCompare(a));

  sortedDates.forEach(date => {
    const items = groups[date].sort((a, b) => b.time.localeCompare(a.time));
    let dIn = 0, dOut = 0;
    items.forEach(i => { i.type === 'income' ? dIn += i.amount : dOut += i.amount; });

    const group = document.createElement('div');
    group.className = 'day-group';
    group.innerHTML = `
      <div class="day-header">
        <span class="day-date">${fmtCNDate(date)} ${weekDay(date)}</span>
        <span class="day-sum">
          ${dIn > 0 ? `<span class="d-income">收 +${fmtAmount(dIn)}</span>` : ''}
          ${dOut > 0 ? `<span class="d-expense">支 -${fmtAmount(dOut)}</span>` : ''}
        </span>
      </div>
    `;
    items.forEach(b => {
      const cat = getCat(b.type, b.category);
      const item = document.createElement('div');
      item.className = 'bill-item';
      item.dataset.id = b.id;
      item.innerHTML = `
        <div class="bill-icon">${cat.emoji}</div>
        <div class="bill-info">
          <div class="bill-category">${cat.name}</div>
          ${b.note ? `<div class="bill-note">${escapeHtml(b.note)}</div>` : ''}
        </div>
        <div class="bill-amount ${b.type}">${b.type === 'income' ? '+' : '-'}${fmtAmount(b.amount)}</div>
      `;
      item.addEventListener('click', () => openEdit(b.id));
      group.appendChild(item);
    });
    listEl.appendChild(group);
  });
}

function escapeHtml(s) {
  const div = document.createElement('div');
  div.textContent = s;
  return div.innerHTML;
}

/* ============ 渲染：分类统计 ============ */
function renderStats() {
  const bills = Store.getAll().filter(b =>
    isSameMonth(b.date, state.curYear, state.curMonth) && b.type === state.statsType
  );
  const listEl = document.getElementById('statsList');
  const emptyEl = document.getElementById('statsEmpty');
  listEl.innerHTML = '';

  if (bills.length === 0) {
    emptyEl.classList.remove('hidden');
    return;
  }
  emptyEl.classList.add('hidden');

  // 按分类汇总
  const agg = {};
  bills.forEach(b => {
    agg[b.category] = (agg[b.category] || 0) + b.amount;
  });
  const total = Object.values(agg).reduce((s, v) => s + v, 0);
  const sorted = Object.entries(agg).sort((a, b) => b[1] - a[1]);

  sorted.forEach(([key, amount]) => {
    const cat = getCat(state.statsType, key);
    const pct = total > 0 ? (amount / total * 100).toFixed(1) : 0;
    const card = document.createElement('div');
    card.className = 'stat-card';
    card.innerHTML = `
      <div class="stat-head">
        <div class="stat-icon">${cat.emoji}</div>
        <div class="stat-name">${cat.name}</div>
        <div class="stat-amount ${state.statsType}">${state.statsType === 'income' ? '+' : '-'}${fmtAmount(amount)}</div>
        <span class="stat-percent">${pct}%</span>
      </div>
      <div class="stat-bar">
        <div class="stat-bar-fill ${state.statsType}" style="width:${pct}%"></div>
      </div>
    `;
    listEl.appendChild(card);
  });
}

/* ============ 弹窗：新增 ============ */
function openAddModal() {
  state.currentType = 'expense';
  state.selectedCategory = null;
  document.getElementById('amountInput').value = '';
  document.getElementById('noteInput').value = '';
  document.getElementById('dateInput').value = fmtDate(new Date());
  renderTypeBtns('add');
  renderCategoryGrid('add');
  document.getElementById('addModal').classList.remove('hidden');
  // 自动聚焦金额
  setTimeout(() => document.getElementById('amountInput').focus(), 100);
}

function closeAddModal() {
  document.getElementById('addModal').classList.add('hidden');
}

function renderTypeBtns(mode, presetType) {
  const modal = mode === 'add' ? 'addModal' : 'editModal';
  const container = document.querySelector(`#${modal} .type-switch`);
  const btns = container.querySelectorAll('.type-btn');
  const cur = mode === 'add' ? state.currentType : state.editType;
  btns.forEach(b => {
    const t = b.dataset.type;
    b.classList.toggle('active', t === cur);
  });
}

function renderCategoryGrid(mode, presetKey) {
  const grid = document.getElementById(mode === 'add' ? 'categoryGrid' : 'editCategoryGrid');
  const type = mode === 'add' ? state.currentType : state.editType;
  const selected = mode === 'add' ? state.selectedCategory : state.editCategory;
  grid.innerHTML = '';
  CATEGORIES[type].forEach(cat => {
    const el = document.createElement('div');
    el.className = 'category-item';
    if ((presetKey && cat.key === presetKey) || (!presetKey && selected === cat.key)) {
      el.classList.add('selected');
      if (mode === 'add') state.selectedCategory = cat.key;
      else state.editCategory = cat.key;
    }
    el.innerHTML = `<div class="category-emoji">${cat.emoji}</div><div class="category-name">${cat.name}</div>`;
    el.addEventListener('click', () => {
      if (mode === 'add') state.selectedCategory = cat.key;
      else state.editCategory = cat.key;
      renderCategoryGrid(mode, mode === 'add' ? state.selectedCategory : state.editCategory);
    });
    grid.appendChild(el);
  });
}

/* ============ 保存新增 ============ */
function saveBill() {
  const amount = parseFloat(document.getElementById('amountInput').value);
  if (!amount || amount <= 0) { shake(document.getElementById('amountInput')); return; }
  if (!state.selectedCategory) { shake(document.getElementById('categoryGrid')); return; }
  const note = document.getElementById('noteInput').value.trim();
  const date = document.getElementById('dateInput').value;
  const now2 = new Date();
  const bill = {
    id: genId(),
    type: state.currentType,
    amount: Math.round(amount * 100) / 100,
    category: state.selectedCategory,
    note,
    date,
    time: `${pad(now2.getHours())}:${pad(now2.getMinutes())}`,
  };
  Store.add(bill);
  closeAddModal();
  refresh();
}

/* ============ 弹窗：编辑 ============ */
function openEdit(id) {
  const bill = Store.getAll().find(b => b.id === id);
  if (!bill) return;
  document.getElementById('editId').value = id;
  document.getElementById('editAmount').value = bill.amount;
  document.getElementById('editNote').value = bill.note || '';
  document.getElementById('editDate').value = bill.date;
  state.editType = bill.type;
  state.editCategory = bill.category;
  renderTypeBtns('edit');
  renderCategoryGrid('edit', bill.category);
  document.getElementById('editModal').classList.remove('hidden');
}

function closeEditModal() {
  document.getElementById('editModal').classList.add('hidden');
}

function updateBill() {
  const id = document.getElementById('editId').value;
  const amount = parseFloat(document.getElementById('editAmount').value);
  if (!amount || amount <= 0) { shake(document.getElementById('editAmount')); return; }
  if (!state.editCategory) { shake(document.getElementById('editCategoryGrid')); return; }
  const patch = {
    type: state.editType,
    amount: Math.round(amount * 100) / 100,
    category: state.editCategory,
    note: document.getElementById('editNote').value.trim(),
    date: document.getElementById('editDate').value,
  };
  Store.update(id, patch);
  closeEditModal();
  refresh();
}

function deleteBill() {
  const id = document.getElementById('editId').value;
  if (!confirm('确定删除这条记录吗？')) return;
  Store.remove(id);
  closeEditModal();
  refresh();
}

/* ============ 辅助 ============ */
function shake(el) {
  el.style.transition = 'transform 0.1s';
  el.style.transform = 'translateX(-6px)';
  setTimeout(() => { el.style.transform = 'translateX(6px)'; }, 100);
  setTimeout(() => { el.style.transform = 'translateX(0)'; }, 200);
}

function refresh() {
  renderSummary();
  renderBillList();
  renderStats();
}

/* ============ 事件绑定 ============ */
document.addEventListener('DOMContentLoaded', () => {
  // FAB
  document.getElementById('fabBtn').addEventListener('click', openAddModal);

  // 关闭弹窗
  document.getElementById('modalClose').addEventListener('click', closeAddModal);
  document.getElementById('editClose').addEventListener('click', closeEditModal);
  document.getElementById('addModal').addEventListener('click', e => {
    if (e.target.id === 'addModal') closeAddModal();
  });
  document.getElementById('editModal').addEventListener('click', e => {
    if (e.target.id === 'editModal') closeEditModal();
  });

  // 保存
  document.getElementById('saveBtn').addEventListener('click', saveBill);
  document.getElementById('updateBtn').addEventListener('click', updateBill);
  document.getElementById('deleteBtn').addEventListener('click', deleteBill);

  // 类型切换（新增）
  document.querySelectorAll('#addModal .type-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      state.currentType = btn.dataset.type;
      state.selectedCategory = null;
      renderTypeBtns('add');
      renderCategoryGrid('add');
    });
  });
  // 类型切换（编辑）
  document.querySelectorAll('#editModal .type-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      state.editType = btn.dataset.type;
      state.editCategory = null;
      renderTypeBtns('edit');
      renderCategoryGrid('edit');
    });
  });

  // Tab 切换
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const view = tab.dataset.view;
      document.getElementById('viewList').classList.toggle('active', view === 'list');
      document.getElementById('viewStats').classList.toggle('active', view === 'stats');
    });
  });

  // 统计类型切换
  document.querySelectorAll('.switch-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.switch-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.statsType = btn.dataset.type;
      renderStats();
    });
  });

  // 回车保存（金额输入）
  document.getElementById('amountInput').addEventListener('keydown', e => {
    if (e.key === 'Enter') saveBill();
  });
  document.getElementById('editAmount').addEventListener('keydown', e => {
    if (e.key === 'Enter') updateBill();
  });

  // 阻止数字输入的滚动
  document.querySelectorAll('input[type=number]').forEach(inp => {
    inp.addEventListener('wheel', e => e.preventDefault(), { passive: false });
  });

  // 初始渲染
  refresh();
});

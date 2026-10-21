const search = document.querySelector('#search');
const cards = [...document.querySelectorAll('.software-card')];
search.addEventListener('input', () => {
  const query = search.value.trim().toLocaleLowerCase();
  cards.forEach(card => { card.hidden = !card.dataset.search.toLocaleLowerCase().includes(query); });
  document.querySelector('#no-results').hidden = cards.some(card => !card.hidden) || !query;
});

let toastTimer;
document.querySelectorAll('[data-share]').forEach(button => {
  button.addEventListener('click', async () => {
    const url = new URL(button.dataset.share, location.href);
    try {
      await navigator.clipboard.writeText(url.href);
      const toast = document.querySelector('#toast');
      toast.hidden = false;
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => { toast.hidden = true; }, 2500);
    } catch {
      window.prompt('复制下方链接即可分享：', url.href);
    }
  });
});

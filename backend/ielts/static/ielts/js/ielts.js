function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// helper to set X-CSRFToken header for fetch
function fetchWithCsrf(url, opts) {
    opts = opts || {};
    opts.headers = opts.headers || {};
    const csrftoken = getCookie('csrftoken');
    if (csrftoken) {
        opts.headers['X-CSRFToken'] = csrftoken;
    }
    return fetch(url, opts);
}

// debounce helper
function debounce(fn, wait){
  let t;
  return function(...args){
    clearTimeout(t);
    t = setTimeout(()=>fn.apply(this,args), wait);
  }
}

// small UI helpers
function setTimerProgress(elProgress, percent){
  if(!elProgress) return;
  elProgress.style.width = percent + '%';
}

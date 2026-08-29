// Search page body for target phrases
const phrases = ['toy model', 'rigorous cross-domain unification', 'Rate-Distortion', 'Honest caveat', 'useful', 'claims to be'];
const html = document.body.innerHTML;
const innerText = document.body.innerText;
const results = {};
phrases.forEach(p => {
  results[p] = {
    html_count: (html.match(new RegExp(p.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length,
    html_idx: html.indexOf(p),
    text_count: (innerText.match(new RegExp(p.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length,
    text_idx: innerText.indexOf(p)
  };
});
JSON.stringify(results, null, 2);

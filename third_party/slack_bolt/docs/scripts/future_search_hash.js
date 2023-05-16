var searchTag = "details";

function update_location_to_hidden_hash() {
  const hash = location.hash.substring(1);
  if (!hash) return;
  const details = document.getElementsByTagName(searchTag);
  for (let i = 0; i < details.length; i++) {
    if (details[i].querySelector(`#${hash}`)) {
      details[i].open = true;
      window.location.hash = `#${hash}`;
      break;
    }
  }
}

window.addEventListener("hashchange", update_location_to_hidden_hash);
window.addEventListener("load", update_location_to_hidden_hash);

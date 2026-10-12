(() => {
  const form = document.querySelector('.teacher-register .registration-form');
  if (!form || !window.DataTransfer) return;
  const pending = new Set();
  ['profile_photo', 'banner_photo'].forEach(name => {
    const input = form.querySelector(`[name="${name}"]`);
    if (!input) return;
    input.accept = 'image/jpeg,image/png,image/webp';
    const banner = name === 'banner_photo';
    const width = banner ? 1600 : 400, height = banner ? 600 : 400;
    const panel = document.createElement('div');
    panel.className = 'image-crop'; panel.hidden = true;
    panel.innerHTML = `<p>Crop ${banner ? 'banner' : 'logo'} (${width} × ${height} px)</p><canvas width="${width}" height="${height}" aria-label="Image crop preview"></canvas>
      <label>Zoom <input type="range" min="1" max="3" step="0.01" value="1" data-zoom></label>
      <label>Left / right <input type="range" min="0" max="1" step="0.01" value="0.5" data-x></label>
      <label>Up / down <input type="range" min="0" max="1" step="0.01" value="0.5" data-y></label>
      <button type="button" data-apply>Use cropped image</button> <button type="button" data-cancel>Cancel new image</button><p role="status" data-status></p>`;
    input.after(panel);
    const sizeInfo = document.createElement('p');
    sizeInfo.className = 'field-help image-size';
    sizeInfo.setAttribute('role', 'status');
    const limitText = 'Maximum image size: 10 MB. JPG, PNG or WebP.';
    const megabytes = bytes => (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    sizeInfo.textContent = limitText;
    panel.after(sizeInfo);
    const canvas = panel.querySelector('canvas'), ctx = canvas.getContext('2d');
    const zoom = panel.querySelector('[data-zoom]'), x = panel.querySelector('[data-x]'), y = panel.querySelector('[data-y]');
    const apply = panel.querySelector('[data-apply]'), status = panel.querySelector('[data-status]');
    let img, url, revision = 0;
    function release() { if (url) URL.revokeObjectURL(url); url = null; }
    function draw() {
      if (!img) return;
      const scale = Math.max(width / img.naturalWidth, height / img.naturalHeight) * Number(zoom.value);
      const w = width / scale, h = height / scale;
      ctx.clearRect(0, 0, width, height);
      ctx.drawImage(img, (img.naturalWidth - w) * Number(x.value), (img.naturalHeight - h) * Number(y.value), w, h, 0, 0, width, height);
    }
    panel.addEventListener('input', draw);
    input.addEventListener('change', () => {
      const version = ++revision;
      release(); img = null; pending.delete(input); panel.hidden = true;
      sizeInfo.textContent = limitText;
      const file = input.files[0]; if (!file) return;
      sizeInfo.textContent = 'Selected image: ' + megabytes(file.size) + '. ' + limitText;
      panel.hidden = false; status.textContent = ''; apply.disabled = true; pending.add(input);
      if (file.size > 10 * 1024 * 1024) {
        status.textContent = 'Image too large (' + megabytes(file.size) + '). Maximum allowed: 10 MB. Choose a smaller image.'; return;
      }
      if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
        status.textContent = 'Choose a JPG, PNG or WebP image.'; return;
      }
      const image = new Image(); url = URL.createObjectURL(file);
      image.onload = () => {
        if (version !== revision) return;
        if (image.naturalWidth * image.naturalHeight > 40000000) { status.textContent = 'Choose an image smaller than 40 megapixels.'; release(); return; }
        img = image; zoom.value = '1'; x.value = y.value = '0.5'; draw(); apply.disabled = false; release();
      };
      image.onerror = () => { if (version === revision) { status.textContent = 'This image could not be opened. Choose another image.'; release(); } };
      image.src = url;
    });
    apply.addEventListener('click', () => {
      if (!img) return;
      const version = revision; apply.disabled = true;
      canvas.toBlob(blob => {
        if (version !== revision) return;
        if (!blob) { status.textContent = 'Could not crop this image. Please try again.'; apply.disabled = false; return; }
        try {
          const transfer = new DataTransfer();
          transfer.items.add(new File([blob], `${name}.png`, {type: 'image/png'}));
          input.files = transfer.files; pending.delete(input); panel.hidden = true;
          sizeInfo.textContent = 'Ready to upload: ' + megabytes(blob.size) + ' (cropped). Maximum: 10 MB.';
        } catch (_) { status.textContent = 'Your browser could not apply the crop. Cancel and try another browser.'; apply.disabled = false; }
      }, 'image/png');
    });
    panel.querySelector('[data-cancel]').addEventListener('click', () => {
      revision++; release(); img = null; input.value = ''; pending.delete(input); panel.hidden = true; sizeInfo.textContent = limitText;
    });
  });
  form.addEventListener('submit', event => {
    if (!pending.size) return;
    event.preventDefault();
    const input = pending.values().next().value;
    input.nextElementSibling.querySelector('[data-status]').textContent = 'Use the cropped image or cancel it before saving.';
    input.focus();
  });
})();

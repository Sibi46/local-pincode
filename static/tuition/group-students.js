(() => {
  const form = document.getElementById('add-student');
  if (!form) return;
  const phone = form.elements.phone, details = document.getElementById('student-details');
  const status = document.getElementById('phone-status'), register = document.getElementById('open-register');
  const dialog = document.getElementById('register-student'), registration = document.getElementById('register-student-form');
  const existing = document.getElementById('existing-students'), known = document.getElementById('known-student');
  let serial = 0, records = [];
  details.disabled = true;
  async function post(url, data) {
    const response = await fetch(url, {method:'POST', body:data, headers:{'X-CSRFToken':form.elements.csrfmiddlewaretoken.value}, credentials:'same-origin'});
    if (!(response.headers.get('Content-Type') || '').includes('application/json')) throw new Error('Please sign in again or try again shortly.');
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || Object.values(result.errors || {}).flat().map(e => e.message).join(' ') || 'Please try again.');
    return result;
  }
  phone.addEventListener('input', () => { ++serial; details.disabled = true; register.hidden = true; existing.hidden = true; form.elements.name.value = ''; form.elements.guardian_name.value = ''; status.textContent = ''; });
  async function check() {
    const current = ++serial;
    details.disabled = true; register.hidden = true; existing.hidden = true;
    if (!/^[0-9]{10}$/.test(phone.value.trim())) { status.textContent = 'Enter a 10-digit phone number.'; return; }
    status.textContent = 'Checking number...';
    const data = new FormData(); data.set('phone', phone.value.trim());
    try {
      const result = await post(form.dataset.checkUrl, data);
      if (current !== serial) return;
      details.disabled = !result.registered;
      register.hidden = result.registered;
      status.textContent = result.registered ? 'Registered. Confirm the student and parent names, then add student.' : 'This number is not registered to an active account. Select Register to continue.';
      records = result.students || [];
      known.replaceChildren(new Option('Enter a new student', ''));
      records.forEach((record, index) => known.add(new Option(record.name, index)));
      existing.hidden = !records.length;
      if (records.length === 1 && !form.elements.name.value) {
        known.value = '0'; form.elements.name.value = records[0].name;
        if (!form.elements.guardian_name.value) form.elements.guardian_name.value = records[0].guardian_name;
      }
    } catch (error) { if (current === serial) status.textContent = error.message; }
  }
  document.getElementById('check-phone').addEventListener('click', check);
  known.addEventListener('change', () => {
    const record = known.value === '' ? null : records[Number(known.value)];
    if (record) { form.elements.name.value = record.name; form.elements.guardian_name.value = record.guardian_name; }
  });
  register.addEventListener('click', () => {
    registration.reset(); registration.elements.phone.value = phone.value.trim();
    registration.elements.name.value = form.elements.guardian_name.value;
    document.getElementById('registration-status').textContent = ''; dialog.showModal();
  });
  document.getElementById('close-register').addEventListener('click', () => dialog.close());
  registration.addEventListener('submit', async event => {
    event.preventDefault();
    const button = registration.querySelector('[type="submit"]'), output = document.getElementById('registration-status');
    button.disabled = true; output.textContent = 'Registering...';
    try {
      await post(form.dataset.registerUrl, new FormData(registration));
      registration.reset(); dialog.close(); await check();
    } catch (error) { output.textContent = error.message; }
    finally { button.disabled = false; }
  });
  if (/^[0-9]{10}$/.test(phone.value.trim())) check();
})();

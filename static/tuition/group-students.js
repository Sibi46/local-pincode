(() => {
  const form = document.getElementById('add-student');
  if (!form) return;
  const phone = form.elements.phone, details = document.getElementById('student-details');
  const status = document.getElementById('phone-status'), register = document.getElementById('open-register');
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
  phone.addEventListener('input', () => { ++serial; details.disabled = true; if (register) register.hidden = true; existing.hidden = true; form.elements.name.value = ''; form.elements.guardian_name.value = ''; status.textContent = ''; });
  async function check() {
    const current = ++serial;
    details.disabled = true; if (register) register.hidden = true; existing.hidden = true;
    if (!/^[0-9]{10}$/.test(phone.value.trim())) { status.textContent = 'Enter a 10-digit phone number.'; return; }
    status.textContent = 'Checking number...';
    const data = new FormData(); data.set('phone', phone.value.trim());
    try {
      const result = await post(form.dataset.checkUrl, data);
      if (current !== serial) return;
      details.disabled = !result.registered;
      if (register) register.hidden = result.registered;
      status.textContent = result.registered ? 'Registered. Confirm the student and parent names, then add student.' : (register ? 'This number is not registered. Select Register to continue.' : 'This number is not registered. Please register first, then add the student.');
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
  if (register) {
  const dialog = document.getElementById('register-student');
  const registration = document.getElementById('register-student-form');
  const output = document.getElementById('registration-status');
  const send = document.getElementById('send-student-otp');
  const create = document.getElementById('create-student-account');
  const otpField = document.getElementById('student-otp-field');
  let otpSerial = 0;
  function resetOTP() {
    ++otpSerial; create.disabled = true; otpField.hidden = true;
    registration.elements.otp.value = ''; registration.elements.otp.required = false;
  }
  register.addEventListener('click', () => {
    registration.reset(); resetOTP(); registration.elements.phone.value = phone.value.trim();
    output.textContent = ''; dialog.showModal();
  });
  document.getElementById('close-register').addEventListener('click', () => dialog.close());
  registration.elements.phone.addEventListener('input', () => { resetOTP(); output.textContent = ''; });
  send.addEventListener('click', async () => {
    if (!['name', 'pincode', 'phone'].every(name => registration.elements[name].reportValidity())) return;
    resetOTP(); const current = otpSerial;
    send.disabled = true; output.textContent = 'Sending OTP...';
    try {
      const response = await fetch(registration.dataset.sendUrl, {
        method:'POST', credentials:'same-origin',
        headers:{'Content-Type':'application/json', 'X-CSRFToken':form.elements.csrfmiddlewaretoken.value},
        body:JSON.stringify({phone:registration.elements.phone.value.trim()})
      });
      if (!(response.headers.get('Content-Type') || '').includes('application/json')) throw new Error('Please sign in again or try later.');
      const result = await response.json();
      if (current !== otpSerial) return;
      if (!response.ok || !result.success) throw new Error(result.error || 'Could not send OTP.');
      otpField.hidden = false; registration.elements.otp.required = true; create.disabled = false;
      output.textContent = 'OTP sent. Enter it within 10 minutes.'; registration.elements.otp.focus();
    } catch (error) { if (current === otpSerial) output.textContent = error.message; }
    finally { send.disabled = false; }
  });
  registration.addEventListener('submit', async event => {
    event.preventDefault();
    if (create.disabled || !registration.reportValidity()) return;
    create.disabled = true; output.textContent = 'Creating account...';
    try {
      await post(registration.dataset.createUrl, new FormData(registration));
      phone.value = registration.elements.phone.value.trim();
      registration.reset(); dialog.close(); await check();
    } catch (error) { output.textContent = error.message; create.disabled = false; }
  });
  }
  if (/^[0-9]{10}$/.test(phone.value.trim())) check();
})();

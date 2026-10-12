(() => {
  const form = document.getElementById('student-form');
  if (!form) return;
  const dob = form.querySelector('[name="dob"]'), age = form.querySelector('[name="age"]');
  const today = form.dataset.today.split('-').map(Number);
  function updateAge() {
    age.readOnly = !!dob.value;
    if (!dob.value) return;
    const birth = dob.value.split('-').map(Number);
    const years = today[0] - birth[0] - (today[1] < birth[1] || (today[1] === birth[1] && today[2] < birth[2]) ? 1 : 0);
    age.value = years >= 0 && years <= 120 ? years : '';
  }
  const self = form.querySelector('[name="self_registration"]');
  function guardianFields() {
    const minor = age.value !== '' && Number(age.value) >= 0 && Number(age.value) < 18;
    const guardian = form.querySelector('[name="guardian_name"]');
    if (guardian) {
      guardian.closest('[data-student-field]').hidden = !minor;
      guardian.disabled = !minor; guardian.required = minor;
      const label = form.querySelector('label[for="'+guardian.id+'"]');
      if (label) label.textContent = 'Parent / guardian name *';
    }
    const phone = form.querySelector('[name="phone"]');
    if (phone) {
      phone.required = minor;
      const label = form.querySelector('label[for="'+phone.id+'"]');
      if (label) label.textContent = minor ? 'Parent / guardian phone *' : 'Phone (optional)';
    }
    if (self && minor) self.checked = false;
    if (!self) return;
    for (const name of ['relationship', 'attestation']) {
      const field = form.querySelector('[name="'+name+'"]');
      if (!field) continue;
      field.required = !self.checked; field.disabled = self.checked;
      field.closest('[data-student-field]').hidden = self.checked;
    }
  }
  if(self) self.addEventListener('change', guardianFields);
  guardianFields();
  dob.addEventListener('input', () => { updateAge(); guardianFields(); });
  age.addEventListener('input', guardianFields);
  updateAge(); guardianFields();
})();

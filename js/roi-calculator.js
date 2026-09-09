/**
 * Autogram Interactive ROI & Agency Cost-Savings Calculator
 */

(function () {
  const postsSlider = document.getElementById('posts-slider');
  const spendSlider = document.getElementById('spend-slider');

  const postsVal = document.getElementById('posts-val');
  const spendVal = document.getElementById('spend-val');

  const annualSavingsEl = document.getElementById('roi-annual-savings');
  const hoursSavedEl = document.getElementById('roi-hours-saved');
  const costPerPostEl = document.getElementById('roi-cost-per-post');

  function calculateROI() {
    if (!postsSlider || !spendSlider) return;

    const posts = parseInt(postsSlider.value, 10);
    const spend = parseInt(spendSlider.value, 10);

    if (postsVal) postsVal.textContent = `${posts} Carousels / mo`;
    if (spendVal) spendVal.textContent = `$${spend.toLocaleString()} / mo`;

    // Calculation logic
    const autogramPlanCost = 997; // Growth autopilot baseline
    const monthlySavings = Math.max(0, spend - autogramPlanCost);
    const annualSavings = monthlySavings * 12;

    const hoursSaved = Math.round(posts * 3.5); // Average 3.5 hrs per bespoke carousel
    const costPerPostAutogram = Math.round(autogramPlanCost / posts);

    if (annualSavingsEl) annualSavingsEl.textContent = `$${annualSavings.toLocaleString()}`;
    if (hoursSavedEl) hoursSavedEl.textContent = `${hoursSaved} hrs`;
    if (costPerPostEl) costPerPostEl.textContent = `$${costPerPostAutogram}`;
  }

  if (postsSlider) postsSlider.addEventListener('input', calculateROI);
  if (spendSlider) spendSlider.addEventListener('input', calculateROI);

  calculateROI();
})();

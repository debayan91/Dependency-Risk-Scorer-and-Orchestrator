/**
 * Minimalist Frontend Logic for SCDS.
 * Zero animations, monochrome UI, purely functional.
 */

document.addEventListener('DOMContentLoaded', () => {
  const tabButtons = document.querySelectorAll('.nav-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  const presetNpmBtn = document.getElementById('preset-npm-btn');
  const presetPypiBtn = document.getElementById('preset-pypi-btn');
  const presetMavenBtn = document.getElementById('preset-maven-btn');

  const manifestFilenameInput = document.getElementById('manifest-filename-input');
  const manifestTextInput = document.getElementById('manifest-text-input');
  const fileUploadInput = document.getElementById('file-upload-input');
  const browseFileBtn = document.getElementById('browse-file-btn');

  const failOnSelect = document.getElementById('fail-on-select');
  const thresholdInput = document.getElementById('threshold-input');
  const triggerScanBtn = document.getElementById('trigger-scan-btn');
  const btnSpinner = triggerScanBtn.querySelector('.btn-spinner');
  const btnText = triggerScanBtn.querySelector('.btn-text');

  const resultsContainer = document.getElementById('results-container');
  const ciGateBanner = document.getElementById('ci-gate-banner');
  const gateTitle = document.getElementById('gate-title');
  const gateReason = document.getElementById('gate-reason');
  const exportJsonBtn = document.getElementById('export-json-btn');

  const kpiTotalScanned = document.getElementById('kpi-total-scanned');
  const kpiCriticalCount = document.getElementById('kpi-critical-count');
  const kpiHighCount = document.getElementById('kpi-high-count');
  const kpiTypoCount = document.getElementById('kpi-typo-count');
  const kpiAvgScore = document.getElementById('kpi-avg-score');

  const filterButtons = document.querySelectorAll('.filter-btn');
  const searchInput = document.getElementById('table-search-input');
  const tableBody = document.getElementById('dependencies-tbody');

  const singlePkgName = document.getElementById('single-pkg-name');
  const singlePkgVersion = document.getElementById('single-pkg-version');
  const singlePkgEcosystem = document.getElementById('single-pkg-ecosystem');
  const singlePkgSubmitBtn = document.getElementById('single-pkg-submit-btn');
  const singleResultContainer = document.getElementById('single-result-container');

  let currentScanReport = null;
  let activeSeverityFilter = 'ALL';

  // Tabs
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      tabButtons.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const targetContent = document.getElementById(btn.getAttribute('data-tab'));
      if (targetContent) targetContent.classList.add('active');
    });
  });

  // Presets
  async function loadPreset(sampleId) {
    try {
      const resp = await fetch(`/api/samples/${sampleId}`);
      if (!resp.ok) return;
      const data = await resp.json();
      manifestFilenameInput.value = data.filename;
      manifestTextInput.value = data.content;
    } catch (_) {}
  }

  presetNpmBtn.addEventListener('click', () => loadPreset('npm_compromised'));
  presetPypiBtn.addEventListener('click', () => loadPreset('pypi_vulnerable'));
  presetMavenBtn.addEventListener('click', () => loadPreset('maven_sample'));

  // Default preset
  loadPreset('npm_compromised');

  // File upload
  browseFileBtn.addEventListener('click', () => fileUploadInput.click());
  fileUploadInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    manifestFilenameInput.value = file.name;
    const reader = new FileReader();
    reader.onload = (evt) => { manifestTextInput.value = evt.target.result; };
    reader.readAsText(file);
  });

  // Scan
  triggerScanBtn.addEventListener('click', async () => {
    const content = manifestTextInput.value.trim();
    if (!content) return;

    const filename = manifestFilenameInput.value.trim() || 'manifest.txt';
    const failOn = failOnSelect.value || null;
    const thresholdVal = thresholdInput.value ? parseFloat(thresholdInput.value) : null;

    btnSpinner.classList.remove('hidden');
    btnText.textContent = 'Scanning...';
    triggerScanBtn.disabled = true;

    try {
      const resp = await fetch('/api/scan/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          filename,
          fail_on: failOn,
          threshold: thresholdVal
        })
      });

      if (!resp.ok) throw new Error('Scan failed');
      const report = await resp.json();
      currentScanReport = report;
      renderScanResults(report);
      resultsContainer.classList.remove('hidden');
    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      btnSpinner.classList.add('hidden');
      btnText.textContent = 'Scan';
      triggerScanBtn.disabled = false;
    }
  });

  function renderScanResults(report) {
    if (report.failed_ci) {
      gateTitle.textContent = 'GATE: BLOCKED';
      gateReason.textContent = report.fail_reason || 'Threshold violated.';
    } else {
      gateTitle.textContent = 'GATE: PASSED';
      gateReason.textContent = 'Dependencies passed policy.';
    }

    kpiTotalScanned.textContent = report.dependencies_scanned;
    const summary = report.risk_summary || {};
    kpiCriticalCount.textContent = summary.CRITICAL || 0;
    kpiHighCount.textContent = summary.HIGH || 0;
    kpiTypoCount.textContent = report.results.filter(r => r.typosquatting_info && r.typosquatting_info.is_typosquat).length;
    kpiAvgScore.textContent = report.avg_risk_score !== undefined ? report.avg_risk_score.toFixed(1) : '0.0';

    document.getElementById('count-all').textContent = report.results.length;
    document.getElementById('count-critical').textContent = summary.CRITICAL || 0;
    document.getElementById('count-high').textContent = summary.HIGH || 0;
    document.getElementById('count-medium').textContent = summary.MEDIUM || 0;
    document.getElementById('count-low').textContent = summary.LOW || 0;
    document.getElementById('count-safe').textContent = summary.SAFE || 0;

    renderTableRows();
  }

  function renderTableRows() {
    if (!currentScanReport) return;
    tableBody.innerHTML = '';
    const query = searchInput.value.toLowerCase().trim();

    const filtered = currentScanReport.results.filter(item => {
      if (activeSeverityFilter !== 'ALL' && item.risk_level !== activeSeverityFilter) return false;
      if (query) {
        return item.name.toLowerCase().includes(query) ||
               item.findings.some(f => f.toLowerCase().includes(query));
      }
      return true;
    });

    if (filtered.length === 0) {
      const emptyRow = document.createElement('tr');
      emptyRow.innerHTML = `<td colspan="7" style="text-align: center; padding: 1.5rem; color: #888;">No items.</td>`;
      tableBody.appendChild(emptyRow);
      return;
    }

    filtered.forEach((r, idx) => {
      const tr = document.createElement('tr');
      tr.className = 'row-item';
      tr.setAttribute('data-index', idx);

      const findingSummary = r.findings.length > 0 ? r.findings[0] : 'Verified clean.';

      tr.innerHTML = `
        <td><span class="toggle-icon">▶</span></td>
        <td><strong>${escapeHtml(r.name)}</strong> ${r.is_dev ? '<span style="font-size:0.7rem; color:#888;">(dev)</span>' : ''}</td>
        <td>${escapeHtml(r.version || 'unpinned')}</td>
        <td>${escapeHtml(r.ecosystem)}</td>
        <td class="score-badge">${r.total_risk_score.toFixed(1)}</td>
        <td><span class="level-badge">${r.risk_level}</span></td>
        <td><div style="font-size: 0.8rem; color: #333;">${escapeHtml(findingSummary)}</div></td>
      `;

      const detailTr = document.createElement('tr');
      detailTr.className = 'detail-row hidden';

      const vScore = (r.breakdown && r.breakdown.vulnerability_score) || 0;
      const tScore = (r.breakdown && r.breakdown.typosquatting_score) || 0;
      const mScore = (r.breakdown && r.breakdown.maintainer_score) || 0;

      let findingsHtml = r.findings.map(f => `<div class="detail-item">• ${escapeHtml(f)}</div>`).join('');
      let recsHtml = r.recommendations.map(rec => `<div class="detail-item">→ ${escapeHtml(rec)}</div>`).join('');

      detailTr.innerHTML = `
        <td colspan="7">
          <div class="detail-grid">
            <div>
              <div style="font-weight: 400; margin-bottom: 0.5rem;">Scores:</div>
              <div>Vulnerability: ${vScore.toFixed(1)} / 10</div>
              <div>Typosquatting: ${tScore.toFixed(1)} / 10</div>
              <div>Maintainer: ${mScore.toFixed(1)} / 10</div>
              ${r.vulnerabilities.length > 0 ? `
                <div style="margin-top: 0.5rem;">Advisories: ${r.vulnerabilities.map(v => v.id).join(', ')}</div>
              ` : ''}
            </div>
            <div>
              <div style="font-weight: 400; margin-bottom: 0.5rem;">Details & Remediation:</div>
              ${findingsHtml}
              ${recsHtml ? `<div style="margin-top: 0.5rem;">${recsHtml}</div>` : ''}
            </div>
          </div>
        </td>
      `;

      tr.addEventListener('click', () => {
        const isExp = tr.classList.toggle('expanded');
        if (isExp) detailTr.classList.remove('hidden');
        else detailTr.classList.add('hidden');
      });

      tableBody.appendChild(tr);
      tableBody.appendChild(detailTr);
    });
  }

  filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      filterButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeSeverityFilter = btn.getAttribute('data-filter');
      renderTableRows();
    });
  });

  searchInput.addEventListener('input', () => renderTableRows());

  exportJsonBtn.addEventListener('click', () => {
    if (!currentScanReport) return;
    const blob = new Blob([JSON.stringify(currentScanReport, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scds-report.json`;
    a.click();
    URL.revokeObjectURL(url);
  });

  // Single package
  singlePkgSubmitBtn.addEventListener('click', async () => {
    const name = singlePkgName.value.trim();
    if (!name) return;
    const version = singlePkgVersion.value.trim() || null;
    const ecosystem = singlePkgEcosystem.value;

    singlePkgSubmitBtn.textContent = '...';
    singlePkgSubmitBtn.disabled = true;

    try {
      const resp = await fetch('/api/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, version, ecosystem })
      });
      if (!resp.ok) throw new Error('Failed');
      const data = await resp.json();

      let findingsHtml = data.findings.map(f => `<div>• ${escapeHtml(f)}</div>`).join('');
      let recsHtml = data.recommendations.map(r => `<div>→ ${escapeHtml(r)}</div>`).join('');

      singleResultContainer.innerHTML = `
        <div style="margin-bottom: 0.75rem;">
          <strong>${escapeHtml(data.name)}</strong> (${escapeHtml(data.version || 'unpinned')}) - 
          Score: <strong>${data.total_risk_score.toFixed(1)}/10</strong> [${data.risk_level}]
        </div>
        <div style="font-size: 0.85rem; margin-bottom: 0.5rem;">
          Vuln: ${data.breakdown.vulnerability_score.toFixed(1)} | 
          Typo: ${data.breakdown.typosquatting_score.toFixed(1)} | 
          Maint: ${data.breakdown.maintainer_score.toFixed(1)}
        </div>
        <div style="font-size: 0.85rem;">
          ${findingsHtml}
          ${recsHtml ? `<div style="margin-top: 0.5rem;">${recsHtml}</div>` : ''}
        </div>
      `;
      singleResultContainer.classList.remove('hidden');
    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      singlePkgSubmitBtn.textContent = 'Audit';
      singlePkgSubmitBtn.disabled = false;
    }
  });

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});

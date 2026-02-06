document.addEventListener('DOMContentLoaded', () => {
    loadArchive();
});

async function decodeNotam() {
    const rawText = document.getElementById('notamInput').value;
    if (!rawText) return;

    try {
        const response = await fetch('/api/notams', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ raw_text: rawText })
        });
        const result = await response.json();

        if (result.success) {
            renderNotam(result.data, 'currentNotam');
            document.getElementById('decodedResult').style.display = 'block';
            loadArchive(); // Refresh archive
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to decode NOTAM');
    }
}

async function fetchApi() {
    // Mock API call filling the textarea
    const mockNotam = `A1234/23 NOTAMN
Q) EPWW/QFAXX/IV/NBO/A/000/999/5210N02058E005
A) EPWA B) 2310251000 C) 2310251400
E) RWY 11/29 CLSD DUE TO MAINT.`;
    document.getElementById('notamInput').value = mockNotam;
}

async function loadArchive() {
    try {
        const response = await fetch('/api/notams');
        const notams = await response.json();
        const grid = document.getElementById('archiveList');
        grid.innerHTML = '';

        notams.forEach(notam => {
            const parsed = JSON.parse(notam.decoded_json);
            const statusClass = getStatusClass(parsed.status);
            const div = document.createElement('div');
            div.className = 'archive-item';
            div.innerHTML = `
                <div style="display:flex; justify-content:space-between;">
                    <span class="notam-id">${parsed.id || 'UNKNOWN'}</span>
                    <span class="status-badge ${statusClass}">${parsed.status || 'N/A'}</span>
                </div>
                <div style="margin-top:0.5rem; font-size:0.9rem;">${parsed.location || 'N/A'}</div>
            `;
            div.onclick = () => {
                renderNotam(parsed, 'currentNotam');
                document.getElementById('decodedResult').style.display = 'block';
                window.scrollTo({ top: 0, behavior: 'smooth' });
            };
            grid.appendChild(div);
        });
    } catch (error) {
        console.error('Error loading archive:', error);
    }
}

function getStatusClass(status) {
    if (!status) return '';
    const s = status.toUpperCase();
    if (s === 'NEW') return 'status-new';
    if (s === 'REPLACE') return 'status-replace';
    if (s === 'CANCEL') return 'status-cancel';
    return '';
}

function renderNotam(data, elementId) {
    const container = document.getElementById(elementId);
    const statusClass = getStatusClass(data.status);

    // Formatting helper
    const field = (label, value, isBody = false) => `
        <div class="field-group">
            <span class="field-label">${label}</span>
            <div class="field-value ${isBody ? 'text-body' : ''}">${value || '-'}</div>
        </div>
    `;

    container.innerHTML = `
        <div class="card-header">
            <span class="notam-id">${data.id}</span>
            <div>
                <span class="notam-time">${data.type}</span>
                <span class="status-badge ${statusClass}">${data.status || 'N/A'}</span>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            ${field('Location', data.location)}
            ${field('Q-Line', data.q_line)}
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            ${field('Start Time', data.start_time)}
            ${field('End Time', data.end_time)}
        </div>
        ${field('Message', data.text, true)}
        ${data.lower_limit ? field('Lower Limit', data.lower_limit) : ''}
        ${data.upper_limit ? field('Upper Limit', data.upper_limit) : ''}
    `;
}

async function checkImpact() {
    const input = document.getElementById('scheduleInput').value;
    // Basic CSV parsing
    const lines = input.split('\n');
    const flights = [];

    lines.forEach((line) => {
        const parts = line.split(',');
        if (parts.length >= 3) {
            flights.push({
                flight_no: parts[0].trim(),
                dep: parts[1].trim(),
                arr: parts[2].trim()
            });
        }
    });

    if (flights.length === 0) {
        alert('No valid flights found. Format: FlightNo, Dep, Arr');
        return;
    }

    try {
        const response = await fetch('/api/check-schedule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ flights })
        });
        const results = await response.json();

        const resultContainer = document.getElementById('impactResults');
        resultContainer.innerHTML = '';

        if (results.length === 0) {
            resultContainer.innerHTML = '<p class="field-label" style="color:var(--success)">No flights impacted by current NOTAMs.</p>';
            return;
        }

        results.forEach(item => {
            const div = document.createElement('div');
            div.className = 'notam-card';
            div.style.borderLeftColor = 'var(--danger)';
            div.innerHTML = `
                <div class="card-header">
                    <span class="notam-id" style="color:var(--text-primary)">${item.flight.flight_no}</span>
                    <span class="notam-time" style="color:var(--danger)">IMPACTED</span>
                </div>
                <div>${item.flight.dep} -> ${item.flight.arr}</div>
                <div style="margin-top:1rem;">
                    <span class="field-label">Affecting NOTAMs:</span>
                    <ul style="padding-left:1rem; margin:0.5rem 0;">
                        ${item.notams.map(n => `<li>${n.id} (${n.location})</li>`).join('')}
                    </ul>
                </div>
            `;
            resultContainer.appendChild(div);
        });

    } catch (error) {
        console.error(error);
        alert('Error checking schedule');
    }
}

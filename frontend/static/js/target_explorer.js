// Target Explorer Logic (Production Rewrite)

document.addEventListener('DOMContentLoaded', () => {
    const searchBtn = document.getElementById('target-search-btn');
    const searchInput = document.getElementById('target-search-input');
    const resultsContainer = document.getElementById('target-results');
    const viewerSection = document.getElementById('viewer-section');

    if (searchBtn) {
        searchBtn.addEventListener('click', () => {
            const query = searchInput.value.trim();
            if (query) performDiscovery(query);
        });

        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const query = searchInput.value.trim();
                if (query) performDiscovery(query);
            }
        });
    }

    async function performDiscovery(uniprotId) {
        // Reset View
        viewerSection.style.display = 'none';
        resultsContainer.innerHTML = `
            <div style="text-align: center; opacity: 0.8; margin-top: 2rem;" class="fade-in">
                <img src="https://upload.wikimedia.org/wikipedia/commons/2/23/DNA_Orbit_Animated.gif" width="100" style="filter: hue-rotate(90deg);">
                <p style="margin-top: 1rem; font-family: monospace; color: var(--primary-color);">[SCANNING UNIPROT] Accessing genomic databanks...</p>
                <div class="scanner-line" style="margin-top:20px; width:200px; margin-left:auto; margin-right:auto;"></div>
            </div>
        `;

        const token = localStorage.getItem('token');
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

        try {
            // Hit the new Production Endpoint
            const response = await fetch(`http://127.0.0.1:8000/api/targets/discover/${encodeURIComponent(uniprotId)}`, {
                method: 'POST',
                headers: headers
            });

            if (response.status === 401) {
                if (window.handleUnauthorized) window.handleUnauthorized();
                throw new Error("Unauthorized: Please login first");
            }

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Database query failed.");
            }

            const targetData = await response.json();
            displayDiscoveryResults(targetData);
            
        } catch (error) {
            console.error('Error:', error);
            resultsContainer.innerHTML = `
                <div style="padding: 1rem; background: rgba(239, 68, 68, 0.1); border: 1px solid var(--danger); text-align: center; border-radius: 8px;" class="fade-in">
                    <p style="color: var(--danger); margin: 0; font-family: monospace;">[EXECUTION ERROR] ${error.message}</p>
                </div>
            `;
        }
    }

    function displayDiscoveryResults(targetData) {
        resultsContainer.innerHTML = '';
        
        const card = document.createElement('div');
        card.className = "glass-card card tech-border fade-in";
        card.style.position = 'relative';

        // Genomic Profile Section
        let sequenceHtml = '';
        if (targetData.sequence) {
             sequenceHtml = `
                <div style="margin-top: 1.5rem; background: var(--background-dark); padding: 1rem; border-radius: 8px; max-height: 150px; overflow-y: auto; border: 1px solid var(--border-color);">
                    <div style="color: var(--text-muted); font-size: 0.8rem; margin-bottom: 0.5rem; font-family: monospace;">// SEQUENCED AMINO ACIDS</div>
                    <div style="font-family: monospace; font-size: 0.85rem; color: #64748b; word-break: break-all;">
                        ${targetData.sequence}
                    </div>
                </div>
             `;
        }

        // ChEMBL Ligands Section
        let ligandsHtml = '';
        if (targetData.known_ligands && targetData.known_ligands.length > 0) {
            const rows = targetData.known_ligands.map(ligand => `
                <tr style="border-bottom: 1px solid var(--border-color);">
                    <td style="padding: 0.75rem; color: var(--primary-color);">${ligand.molecule_chembl_id}</td>
                    <td style="padding: 0.75rem; color: var(--success); font-weight: 600;">${ligand.standard_type}</td>
                    <td style="padding: 0.75rem;">${ligand.standard_value} ${ligand.standard_units}</td>
                    <td style="padding: 0.75rem; font-family: monospace; font-size: 0.8rem; color: #64748b; max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${ligand.smiles}</td>
                </tr>
            `).join('');

            ligandsHtml = `
                <div style="margin-top: 2rem;">
                    <h4 style="color: var(--text-main); margin-bottom: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem;">
                        Identified ChEMBL Binders (${targetData.known_ligands.length})
                    </h4>
                    <div style="overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse; text-align: left;">
                            <thead>
                                <tr>
                                    <th style="padding: 0.5rem; color: var(--text-muted); font-weight: 500; font-size: 0.85rem;">ChEMBL ID</th>
                                    <th style="padding: 0.5rem; color: var(--text-muted); font-weight: 500; font-size: 0.85rem;">Affinity Metric</th>
                                    <th style="padding: 0.5rem; color: var(--text-muted); font-weight: 500; font-size: 0.85rem;">Bioactivity</th>
                                    <th style="padding: 0.5rem; color: var(--text-muted); font-weight: 500; font-size: 0.85rem;">SMILES Signature</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rows}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        card.innerHTML = `
            <div class="card-header" style="margin-bottom: 0;">
                <h3 style="font-size: 1.5rem; font-weight: 600; color: var(--text-main); margin: 0;">${targetData.name}</h3>
                <span style="background: rgba(14, 165, 233, 0.1); color: var(--primary-color); padding: 0.25rem 0.75rem; border-radius: 4px; font-weight: bold; font-family: monospace;">
                    ${targetData.uniprot_id || 'UNKNOWN'}
                </span>
            </div>
            <p style="color: var(--text-muted); margin-top: 0.5rem; font-size: 0.95rem;">${targetData.description || 'Protein signature retrieved.'}</p>
            
            ${sequenceHtml}
            ${ligandsHtml}
        `;

        resultsContainer.appendChild(card);
        
        // Trigger generic 3DMol Rendering Pipeline
        render3DStructure(targetData);
    }

    function render3DStructure(targetData) {
        const container = document.getElementById('mol-viewer');
        const titleHeader = document.querySelector('#viewer-section h3');
        const sourceBadge = document.querySelector('#viewer-section span');

        viewerSection.style.display = 'block';
        container.innerHTML = ''; // clear previous render
        container.style.display = 'block'; // ensure visible if it was hidden by alphafold fallback warning

        let pdbId = null;
        let pbdResolutionType = "INTERACTIVE";
        
        // Prefer true PDB crystals
        if (targetData.pdb_ids && targetData.pdb_ids.length > 0) {
            pdbId = targetData.pdb_ids[0]; // grab the highest resolution first
            pbdResolutionType = "RCSB PDB CRYSTAL";
        }

        // Update UI Labels
        titleHeader.innerText = `>>> MOLECULAR_VISUALIZATION_MODULE [${pdbId || 'SEARCHING'}]`;
        sourceBadge.innerText = (targetData.properties?.structural_source || pbdResolutionType).toUpperCase();

        if (pdbId) {
            const viewer = $3Dmol.createViewer(container, { backgroundColor: '#0f172a' });
            $3Dmol.download(`pdb:${pdbId}`, viewer, {
                multimodel: true,
                frames: true
            }, function () {
                viewer.setStyle({}, { cartoon: { color: 'spectrum' } });
                viewer.zoomTo();
                viewer.render();
                viewer.spin(true);
            });
            setTimeout(() => viewerSection.scrollIntoView({ behavior: 'smooth' }), 200);
        } else if (targetData.alphafold_url) {
            // Load AlphaFold PDB directly from URL
            const viewer = $3Dmol.createViewer(container, { backgroundColor: '#0f172a' });
            // By default alphafold gives a .pdb appended string
            const plddtToColor = function(atom) {
                 if (atom.b > 90) return '#0053D6'; // Very high
                 if (atom.b > 70) return '#65CBF3'; // Confident
                 if (atom.b > 50) return '#FFE000'; // Low
                 return '#FF7D45'; // Very low
            };

            $3Dmol.download(targetData.alphafold_url, viewer, { format: 'pdb' }, function () {
                viewer.setStyle({}, { cartoon: { colorfunc: plddtToColor } });
                viewer.zoomTo();
                viewer.render();
                viewer.spin(true);
            });
            setTimeout(() => viewerSection.scrollIntoView({ behavior: 'smooth' }), 200);
        } else {
             container.innerHTML = `
                <div style="display:flex; justify-content:center; align-items:center; height:100%; color:var(--text-muted); flex-direction:column; background: #020617; border-radius: 8px;">
                    <div style="font-size:3rem; margin-bottom:1rem;">🧬</div>
                    <div style="font-family: monospace;">[CRITICAL] No 3D topology matrices available for mapping.</div>
                </div>
             `;
             setTimeout(() => viewerSection.scrollIntoView({ behavior: 'smooth' }), 200);
        }
    }
});

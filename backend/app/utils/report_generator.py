from fpdf import FPDF
from datetime import datetime
import io

class PDFReport(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 20)
        # Colors: Deep Blue
        self.set_text_color(26, 35, 126)
        # Title
        self.cell(0, 10, 'Biologics Discovery Platform', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.set_text_color(100)
        self.cell(0, 10, 'Advanced Molecular Analysis & Formulation Report', 0, 1, 'C')
        # Line break
        self.ln(5)
        # Blue horizontal line
        self.set_draw_color(26, 35, 126)
        self.set_line_width(1)
        self.line(10, 32, 200, 32)
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')
        # Date
        self.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'R')

def generate_preformulation_pdf(data):
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Section Header
    pdf.set_fill_color(232, 234, 246)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, ' PREFORMULATION ANALYSIS REPORT', 0, 1, 'L', fill=True)
    pdf.ln(5)
    
    # Compound Info
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(50, 8, 'Compound ID:', 0, 0)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, str(data.get('compound_id')), 0, 1)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(50, 8, 'SMILES:', 0, 0)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 8, str(data.get('smiles')))
    pdf.ln(5)
    
    # Physicochemical Properties Table
    pdf.set_fill_color(26, 35, 126)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, ' Physicochemical Properties', 0, 1, 'L', fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 11)
    
    props = [
        ('Molecular Weight', f"{data.get('molecular_weight')} g/mol"),
        ('LogP', str(data.get('logp'))),
        ('TPSA', f"{data.get('tpsa')} A^2"),
        ('H-Bond Donors', str(data.get('h_bond_donors'))),
        ('H-Bond Acceptors', str(data.get('h_bond_acceptors'))),
        ('Rotatable Bonds', str(data.get('rotatable_bonds'))),
        ('Solubility Prediction', str(data.get('solubility_prediction'))),
    ]
    
    fill = False
    for label, value in props:
        pdf.set_fill_color(245, 245, 245)
        pdf.cell(60, 8, label, 1, 0, 'L', fill=fill)
        pdf.cell(130, 8, value, 1, 1, 'L', fill=fill)
        fill = not fill
        
    pdf.ln(10)
    
    # Drug Likeness
    pdf.set_fill_color(26, 35, 126)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, ' Drug Likeness Assessment', 0, 1, 'L', fill=True)
    pdf.set_text_color(0, 0, 0)
    
    status = data.get('drug_likeness_status')
    if status == 'Pass':
        pdf.set_text_color(46, 125, 50) # Green
    else:
        pdf.set_text_color(198, 40, 40) # Red
        
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(60, 8, 'Status:', 0, 0)
    pdf.cell(0, 8, status, 0, 1)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font('Arial', '', 11)
    pdf.cell(60, 8, 'Lipinski Violations:', 0, 0)
    pdf.cell(0, 8, str(data.get('lipinski_violations')), 0, 1)
    pdf.cell(60, 8, 'Veber Violations:', 0, 0)
    pdf.cell(0, 8, str(data.get('veber_violations')), 0, 1)
    
    pdf.ln(10)
    
    # Risks and Recommendations
    pdf.set_fill_color(26, 35, 126)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(190, 10, ' Potential Risks & Stability Assessment', 0, 1, 'L', fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 11)
    
    risks = data.get('stability_risk', [])
    if not risks:
        pdf.cell(0, 8, 'No significant stability risks identified.', 0, 1)
    else:
        for risk in risks:
            pdf.multi_cell(0, 8, f"- {risk}")
            
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, 'Recommended Excipients:', 0, 1)
    pdf.set_font('Arial', '', 11)
    excipients = data.get('recommended_excipients', [])
    pdf.cell(0, 8, ", ".join(excipients), 0, 1)
    
    return bytes(pdf.output(dest='S'))

def generate_formulation_pdf(form_data, pre_data):
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Section Header
    pdf.set_fill_color(232, 234, 246)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, ' FORMULATION STRATEGY REPORT', 0, 1, 'L', fill=True)
    pdf.ln(5)
    
    # Compound Info Summary
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(50, 8, 'Compound ID:', 0, 0)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, str(form_data.get('compound_id')), 0, 1)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(50, 8, 'Molecular Weight:', 0, 0)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f"{pre_data.get('molecular_weight')} g/mol", 0, 1)
    pdf.ln(5)
    
    # Formulation Design Table
    pdf.set_fill_color(26, 35, 126)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, ' Final Formulation Design', 0, 1, 'L', fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 11)
    
    design_props = [
        ('Formulation Type', str(form_data.get('formulation_type'))),
        ('Drug Concentration', str(form_data.get('drug_concentration'))),
        ('Required Buffer', str(form_data.get('buffer'))),
        ('Stabilizer System', str(form_data.get('stabilizer'))),
        ('Surfactant', str(form_data.get('surfactant'))),
        ('Recommended pH', str(form_data.get('recommended_ph'))),
    ]
    
    fill = False
    for label, value in design_props:
        pdf.set_fill_color(245, 245, 245)
        pdf.cell(65, 10, label, 1, 0, 'L', fill=fill)
        pdf.cell(125, 10, value, 1, 1, 'L', fill=fill)
        fill = not fill
        
    pdf.ln(10)
    
    # Scientific Rationale
    pdf.set_fill_color(26, 35, 126)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, ' Scientific Rationale & Refinement Notes', 0, 1, 'L', fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 11)
    
    rationale = []
    solubility = pre_data.get('solubility_prediction')
    if solubility in ['Low', 'Very Low']:
        rationale.append(f"Due to {solubility} solubility, a surfactant ({form_data.get('surfactant')}) is included to ensure proper dissolution.")
    
    risks = pre_data.get('stability_risk', [])
    if any("hygroscopicity" in r for r in risks):
        rationale.append("High hygroscopicity risk detected; Sucrose is used as a stabilizer over Trehalose.")
    else:
        rationale.append("Stability risks are manageable; Trehalose is used for cryoprotection/stabilization.")
        
    for r in rationale:
        pdf.multi_cell(0, 8, f"- {r}")
        
    pdf.ln(5)
    pdf.set_font('Arial', 'I', 10)
    pdf.multi_cell(0, 8, "Note: This formulation design is AI-generated based on predicted molecular properties. Physical stability testing and compatibility studies (DSC, TGA, HPLC) are recommended for final validation.")

    return bytes(pdf.output(dest='S'))

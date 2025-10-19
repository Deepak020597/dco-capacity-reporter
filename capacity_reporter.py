import json

# --- Configuration ---
DATA_FILE = 'dcim_data.json'
MAX_RACK_UNITS = 42
MAX_RACK_POWER_KVA = 5.0 # 5,000 Watts or 5.0 kVA
EOL_AGE_YEARS = 5.0
CRITICAL_VENDORS = ['HP', 'EMC']

def load_data(filename):
    # Loads the simulated DCIM asset data from a JSON file
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # In a real scenario, this would handle a missing file. 
        # In GitHub web, we assume it's committed.
        print(f"Error: Data file {filename} not found.")
        return []

def analyze_capacity(assets):
    # Aggregates capacity metrics (U-space and Power)
    
    total_assets = len(assets)
    racks = {}
    
    for asset in assets:
        rack_id = asset['rack_id']
        if rack_id not in racks:
            # Initialize rack metrics
            racks[rack_id] = {
                'units_used': 0,
                'power_used_watts': 0
            }
        
        if asset['status'] == 'Online':
             racks[rack_id]['units_used'] += asset['rack_units']
             racks[rack_id]['power_used_watts'] += asset['power_watts']
             
    # Calculate utilization and identify compliance issues
    capacity_metrics = []
    total_power_used_watts = 0
    
    for rack_id, metrics in racks.items():
        power_used_kva = metrics['power_used_watts'] / 1000.0
        power_utilization = (power_used_kva / MAX_RACK_POWER_KVA) * 100
        units_utilization = (metrics['units_used'] / MAX_RACK_UNITS) * 100
        total_power_used_watts += metrics['power_used_watts']
        
        capacity_metrics.append({
            'rack_id': rack_id,
            'units_used': metrics['units_used'],
            'power_used_kva': f"{power_used_kva:.2f}",
            'power_utilization': f"{power_utilization:.1f}%",
            'units_utilization': f"{units_utilization:.1f}%"
        })

    return capacity_metrics, total_assets, total_power_used_watts

def check_compliance_and_eol(assets):
    # Identifies assets nearing End-of-Life (EOL) or high-risk vendors
    
    eol_assets = []
    vendor_risk_assets = []
    
    for asset in assets:
        # EOL Check
        if asset['asset_age_years'] >= EOL_AGE_YEARS and asset['status'] != 'Decom Pending':
            eol_assets.append({
                'id': asset['asset_id'],
                'rack': asset['rack_id'],
                'age': asset['asset_age_years'],
                'status': 'EOL Risk'
            })
            
        # Vendor Risk Check
        if asset['vendor'] in CRITICAL_VENDORS and asset['status'] == 'Online':
            vendor_risk_assets.append({
                'id': asset['asset_id'],
                'rack': asset['rack_id'],
                'vendor': asset['vendor'],
                'age': asset['asset_age_years']
            })

    return eol_assets, vendor_risk_assets
    
def generate_report(capacity_metrics, total_assets, total_power_watts, eol_assets, vendor_risk_assets):
    # Generates a clear, structured report output
    
    report = []
    
    # --- HEADER ---
    report.append("=" * 60)
    report.append("  DCO CAPACITY AND COMPLIANCE REPORT")
    report.append(f"  Total Assets Tracked: {total_assets}")
    report.append(f"  Total Active Power Draw: {total_power_watts / 1000.0:.2f} kVA")
    report.append("=" * 60)
    report.append("\n")

    # --- SECTION 1: RACK CAPACITY UTILIZATION ---
    report.append("--- 1. RACK CAPACITY UTILIZATION (by Rack ID) ---\n")
    report.append(f"{'Rack ID':<10}{'U Used':<10}{'Power (kVA)':<15}{'U Util.':<12}{'Power Util.':<12}")
    report.append("-" * 60)
    for metric in capacity_metrics:
        report.append(f"{metric['rack_id']:<10}{metric['units_used']:<10}{metric['power_used_kva']:<15}{metric['units_utilization']:<12}{metric['power_utilization']:<12}")
    report.append("\n")

    # --- SECTION 2: COMPLIANCE RISKS ---
    report.append("--- 2. COMPLIANCE & END-OF-LIFE RISKS ---\n")
    
    # EOL Assets
    if eol_assets:
        report.append(f"### EOL Assets (Age >= {EOL_AGE_YEARS} Years): {len(eol_assets)} Devices Identified")
        report.append(f"{'Asset ID':<15}{'Rack ID':<10}{'Age (Yrs)':<10}{'Status':<15}")
        report.append("-" * 50)
        for asset in eol_assets:
            report.append(f"{asset['id']:<15}{asset['rack']:<10}{asset['age']:<10.1f}{asset['status']:<15}")
    else:
        report.append("### EOL Assets: 0 devices identified. Compliance maintained.")
        
    report.append("\n")
    
    # High-Risk Vendors
    if vendor_risk_assets:
        report.append(f"### High-Risk Vendor Assets ({', '.join(CRITICAL_VENDORS)}): {len(vendor_risk_assets)} Devices Identified")
        report.append(f"{'Asset ID':<15}{'Rack ID':<10}{'Vendor':<10}{'Age (Yrs)':<10}")
        report.append("-" * 45)
        for asset in vendor_risk_assets:
            report.append(f"{asset['id']:<15}{asset['rack']:<10}{asset['vendor']:<10}{asset['age']:<10.1f}")
    else:
        report.append("### High-Risk Vendors: No active assets from critical vendors identified.")
        
    report.append("\n")
    report.append("--- END OF REPORT ---")
    
    return "\n".join(report)

if __name__ == "__main__":
    assets = load_data(DATA_FILE)
    if assets:
        capacity_metrics, total_assets, total_power_watts = analyze_capacity(assets)
        eol_assets, vendor_risk_assets = check_compliance_and_eol(assets)
        
        report_output = generate_report(
            capacity_metrics, 
            total_assets, 
            total_power_watts, 
            eol_assets, 
            vendor_risk_assets
        )
        
        # When run locally, this prints the output.
        # When viewing the file on GitHub, it just displays the code.
        print(report_output)
    
    

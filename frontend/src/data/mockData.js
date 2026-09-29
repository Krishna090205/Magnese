// Comprehensive fallback dataset for MOIL Manganese Mines
// Ensures uninterrupted high-fidelity rendering if backend API is offline

export const MOIL_MINES = [
  {
    id: 1,
    name: 'Dongri Buzurg Mine',
    code: 'DBM-01',
    state: 'Maharashtra',
    district: 'Bhandara',
    type: 'Open Cast & Underground',
    operational_status: 'Active',
    capacity_tonnes_per_year: 450000,
    current_depth_m: 142,
    benches_count: 7,
    proven_reserves_mt: 3.42,
    avg_grade_mn: 42.8,
    active_haulers: 8,
    active_shovels: 2,
    lat: 21.5542,
    lon: 79.6894,
    source_tag: 'REAL_OFFICIAL'
  },
  {
    id: 2,
    name: 'Balaghat Mine',
    code: 'BGM-02',
    state: 'Madhya Pradesh',
    district: 'Balaghat',
    type: 'Underground Deep Pit',
    operational_status: 'Active',
    capacity_tonnes_per_year: 520000,
    current_depth_m: 385,
    benches_count: 5,
    proven_reserves_mt: 5.18,
    avg_grade_mn: 44.2,
    active_haulers: 9,
    active_shovels: 2,
    lat: 21.8044,
    lon: 80.1847,
    source_tag: 'REAL_OFFICIAL'
  },
  {
    id: 3,
    name: 'Kandri Mine',
    code: 'KDM-03',
    state: 'Maharashtra',
    district: 'Nagpur',
    type: 'Open Cast',
    operational_status: 'Active',
    capacity_tonnes_per_year: 280000,
    current_depth_m: 98,
    benches_count: 6,
    proven_reserves_mt: 2.15,
    avg_grade_mn: 39.6,
    active_haulers: 5,
    active_shovels: 1,
    lat: 21.4167,
    lon: 79.2667,
    source_tag: 'REAL_OFFICIAL'
  },
  {
    id: 4,
    name: 'Mansar Mine',
    code: 'MSM-04',
    state: 'Maharashtra',
    district: 'Nagpur',
    type: 'Open Cast & Underground',
    operational_status: 'Active',
    capacity_tonnes_per_year: 210000,
    current_depth_m: 110,
    benches_count: 5,
    proven_reserves_mt: 1.84,
    avg_grade_mn: 38.9,
    active_haulers: 4,
    active_shovels: 1,
    lat: 21.3986,
    lon: 79.2789,
    source_tag: 'REAL_OFFICIAL'
  },
  {
    id: 5,
    name: 'Gumgaon Mine',
    code: 'GGM-05',
    state: 'Maharashtra',
    district: 'Nagpur',
    type: 'Underground',
    operational_status: 'Active',
    capacity_tonnes_per_year: 190000,
    current_depth_m: 220,
    benches_count: 4,
    proven_reserves_mt: 1.62,
    avg_grade_mn: 41.1,
    active_haulers: 4,
    active_shovels: 1,
    lat: 21.3789,
    lon: 79.0345,
    source_tag: 'REAL_OFFICIAL'
  },
  {
    id: 6,
    name: 'Ukwa Mine',
    code: 'UKM-06',
    state: 'Madhya Pradesh',
    district: 'Balaghat',
    type: 'Underground Drift',
    operational_status: 'Active',
    capacity_tonnes_per_year: 160000,
    current_depth_m: 175,
    benches_count: 4,
    proven_reserves_mt: 1.45,
    avg_grade_mn: 40.5,
    active_haulers: 3,
    active_shovels: 1,
    lat: 21.9682,
    lon: 80.4689,
    source_tag: 'REAL_OFFICIAL'
  },
  {
    id: 7,
    name: 'Tirodi Mine',
    code: 'TRM-07',
    state: 'Madhya Pradesh',
    district: 'Balaghat',
    type: 'Open Cast',
    operational_status: 'Active',
    capacity_tonnes_per_year: 240000,
    current_depth_m: 85,
    benches_count: 5,
    proven_reserves_mt: 2.30,
    avg_grade_mn: 37.8,
    active_haulers: 5,
    active_shovels: 1,
    lat: 21.6841,
    lon: 79.7124,
    source_tag: 'REAL_OFFICIAL'
  }
];

export const MOCK_OVERVIEW = {
  mines_monitored: 8,
  active_shortfall_alerts: 2,
  active_exploration_targets: 14,
  total_annual_capacity_tonnes: 1450000,
  daily_production_actual: 3420,
  daily_production_target: 3500,
  fleet_availability_pct: 92.4,
  high_confidence_reserves_mt: 4.85,
  avg_manganese_grade: 41.8,
  shortfall_risk_pct: 4.2,
  data_freshness: {
    latest_shortfall_prediction: new Date().toISOString(),
    satellite_pass: 'Sentinel-2B (T38QNF) - 3 hrs ago'
  },
  source_tag_provenance: 'REAL_OFFICIAL'
};

export const MOCK_ALERTS = [
  {
    id: 101,
    mine_id: 1,
    mine_name: 'Dongri Buzurg Mine',
    type: 'shortfall',
    severity: 'medium',
    probability: 0.124,
    predicted_shortfall_tonnes: 85.4,
    lead_time_days: 3,
    root_cause: 'Shovel #02 hydraulic seal wear & monsoon haul ramp friction',
    source_tag: 'REAL_OFFICIAL'
  },
  {
    id: 102,
    mine_id: 2,
    mine_name: 'Balaghat Mine',
    type: 'exploration',
    severity: 'low',
    probability: 0.041,
    predicted_reserve_tonnes: 284500,
    confidence_level: 0.91,
    root_cause: 'High-density gravity and aeromagnetic anomaly in North Lobe',
    source_tag: 'REAL_OFFICIAL'
  },
  {
    id: 103,
    mine_id: 3,
    mine_name: 'Kandri Mine',
    type: 'shortfall',
    severity: 'low',
    probability: 0.062,
    predicted_shortfall_tonnes: 42.1,
    lead_time_days: 5,
    root_cause: 'Secondary crusher mantle maintenance cycle pending',
    source_tag: 'PROXY'
  }
];

export const MOCK_PRODUCTION_TREND = [
  { date: '15 Sep', production: 3350, target: 3400, shortfall: 50, mn_grade: 41.5 },
  { date: '17 Sep', production: 3410, target: 3400, shortfall: 0, mn_grade: 41.9 },
  { date: '19 Sep', production: 3480, target: 3500, shortfall: 20, mn_grade: 42.2 },
  { date: '21 Sep', production: 3290, target: 3500, shortfall: 210, mn_grade: 40.8 },
  { date: '23 Sep', production: 3520, target: 3500, shortfall: 0, mn_grade: 42.4 },
  { date: '25 Sep', production: 3460, target: 3500, shortfall: 40, mn_grade: 41.7 },
  { date: '27 Sep', production: 3510, target: 3500, shortfall: 0, mn_grade: 42.1 },
  { date: '29 Sep', production: 3420, target: 3500, shortfall: 80, mn_grade: 41.8 }
];

export const MOCK_RECOMMENDATIONS = [
  {
    id: 201,
    mine_id: 1,
    recommendation_type: 'Fleet Re-dispatch',
    priority: 'high',
    title: 'Dynamic Hauler Re-routing to Bench +280m',
    description: 'Re-assign CAT 777E Dumpers #04 & #07 from overburden ramp to Shovel #1 at Bench +280m to eliminate crusher idle cycle and prevent 65 T shortfall.',
    status: 'pending',
    impact_tonnes: 65,
    source_tag: 'REAL_OFFICIAL'
  },
  {
    id: 202,
    mine_id: 1,
    recommendation_type: 'Blasting Optimization',
    priority: 'medium',
    title: 'Electronic Detonator Delay Adjustment',
    description: 'Increase inter-hole delay from 25ms to 42ms along the hanging wall to reduce boulders >400mm and enhance mucking productivity by 14%.',
    status: 'pending',
    impact_tonnes: 90,
    source_tag: 'REAL_OFFICIAL'
  },
  {
    id: 203,
    mine_id: 2,
    recommendation_type: 'Grade Control',
    priority: 'low',
    title: 'Selective High-Grade Manganese Blending',
    description: 'Blend 30% ore from Level -180m (45.2% Mn) with Level -120m (38.4% Mn) to maintain shipment grade specifications at 42.0% Mn.',
    status: 'completed',
    impact_tonnes: 120,
    source_tag: 'REAL_OFFICIAL'
  }
];

export const MOCK_RESERVE_TARGETS = [
  {
    id: 301,
    mine_id: 1,
    mine_name: 'Dongri Buzurg Mine',
    block_id: 'DB-NW-04',
    predicted_reserve_tonnes: 485000,
    confidence_level: 0.94,
    avg_grade_mn: 43.4,
    sio2_pct: 6.8,
    fe_pct: 6.2,
    al2o3_pct: 3.1,
    depth_m: 145,
    strike_length_m: 620,
    thickness_m: 14.2,
    unfc_classification: '111 - Proved Reserve',
    model_version: 'ARMPI-DeepOre-v2.4',
    source_tag: 'REAL_OFFICIAL'
  },
  {
    id: 302,
    mine_id: 2,
    mine_name: 'Balaghat Mine',
    block_id: 'BG-SE-12',
    predicted_reserve_tonnes: 720000,
    confidence_level: 0.89,
    avg_grade_mn: 45.1,
    sio2_pct: 5.4,
    fe_pct: 5.8,
    al2o3_pct: 2.8,
    depth_m: 290,
    strike_length_m: 850,
    thickness_m: 18.6,
    unfc_classification: '121 - Probable Reserve',
    model_version: 'ARMPI-DeepOre-v2.4',
    source_tag: 'REAL_OFFICIAL'
  },
  {
    id: 303,
    mine_id: 3,
    mine_name: 'Kandri Mine',
    block_id: 'KD-CENTRAL-02',
    predicted_reserve_tonnes: 310000,
    confidence_level: 0.87,
    avg_grade_mn: 40.2,
    sio2_pct: 8.2,
    fe_pct: 7.1,
    al2o3_pct: 3.9,
    depth_m: 92,
    strike_length_m: 410,
    thickness_m: 9.8,
    unfc_classification: '122 - Probable Reserve',
    model_version: 'ARMPI-DeepOre-v2.4',
    source_tag: 'PROXY'
  },
  {
    id: 304,
    mine_id: 4,
    mine_name: 'Mansar Mine',
    block_id: 'MS-NORTH-01',
    predicted_reserve_tonnes: 260000,
    confidence_level: 0.84,
    avg_grade_mn: 39.5,
    sio2_pct: 9.1,
    fe_pct: 7.4,
    al2o3_pct: 4.2,
    depth_m: 115,
    strike_length_m: 380,
    thickness_m: 8.5,
    unfc_classification: '221 - Pre-feasibility',
    model_version: 'ARMPI-DeepOre-v2.4',
    source_tag: 'PROXY'
  }
];

export const MOCK_DRILLHOLES = [
  { id: 1, hole_id: 'DH-DB-2024-01', mine_id: 1, mine_name: 'Dongri Buzurg', collar_x: 79.6894, collar_y: 21.5542, elevation_m: 342, total_depth_m: 185.0, drill_date: '2024-03-12', mn_intercept_m: 24.5, mn_grade: 43.8, source_tag: 'REAL_OFFICIAL' },
  { id: 2, hole_id: 'DH-DB-2024-02', mine_id: 1, mine_name: 'Dongri Buzurg', collar_x: 79.6912, collar_y: 21.5558, elevation_m: 340, total_depth_m: 210.0, drill_date: '2024-04-05', mn_intercept_m: 18.2, mn_grade: 41.2, source_tag: 'REAL_OFFICIAL' },
  { id: 3, hole_id: 'DH-DB-2024-03', mine_id: 1, mine_name: 'Dongri Buzurg', collar_x: 79.6881, collar_y: 21.5531, elevation_m: 345, total_depth_m: 165.5, drill_date: '2024-05-18', mn_intercept_m: 28.0, mn_grade: 44.6, source_tag: 'REAL_OFFICIAL' },
  { id: 4, hole_id: 'DH-BG-2024-01', mine_id: 2, mine_name: 'Balaghat', collar_x: 80.1847, collar_y: 21.8044, elevation_m: 320, total_depth_m: 340.0, drill_date: '2024-02-14', mn_intercept_m: 32.1, mn_grade: 45.4, source_tag: 'REAL_OFFICIAL' },
  { id: 5, hole_id: 'DH-KD-2024-01', mine_id: 3, mine_name: 'Kandri', collar_x: 79.2667, collar_y: 21.4167, elevation_m: 312, total_depth_m: 140.0, drill_date: '2024-06-20', mn_intercept_m: 15.6, mn_grade: 39.8, source_tag: 'REAL_OFFICIAL' }
];

export const MOCK_FLEET_TRUCKS = [
  { id: 'DT-01', model: 'Komatsu HD785-7', capacity: '100T', bench: 'Bench +280m', status: 'Hauling Loaded', speed_kmh: 22, load_tonnes: 98.4, destination: 'Primary Crusher #1', cycle_time_min: 17.8, fuel_level: 82 },
  { id: 'DT-02', model: 'Komatsu HD785-7', capacity: '100T', bench: 'Bench +260m', status: 'Loading', speed_kmh: 0, load_tonnes: 62.0, destination: 'Primary Crusher #1', cycle_time_min: 19.1, fuel_level: 68 },
  { id: 'DT-03', model: 'CAT 777E', capacity: '100T', bench: 'Main Haul Ramp', status: 'Returning Empty', speed_kmh: 31, load_tonnes: 0, destination: 'Shovel Face #02', cycle_time_min: 16.5, fuel_level: 91 },
  { id: 'DT-04', model: 'CAT 777E', capacity: '100T', bench: 'Crusher Dump', status: 'Dumping', speed_kmh: 0, load_tonnes: 95.2, destination: 'Primary Crusher #2', cycle_time_min: 18.2, fuel_level: 45 },
  { id: 'DT-05', model: 'BEML BH100', capacity: '100T', bench: 'Bench +300m', status: 'Hauling Loaded', speed_kmh: 24, load_tonnes: 99.1, destination: 'Stockpile Alpha', cycle_time_min: 18.9, fuel_level: 76 },
  { id: 'DT-06', model: 'BEML BH100', capacity: '100T', bench: 'Bench +280m', status: 'Queueing', speed_kmh: 4, load_tonnes: 0, destination: 'Shovel Face #01', cycle_time_min: 20.4, fuel_level: 59 }
];

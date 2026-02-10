from datetime import datetime
import pandas as pd


class ConflictDetector:
    """Service for detecting conflicts in pilot and drone assignments."""
    
    def __init__(self, sheets_service):
        """Initialize with Google Sheets service."""
        self.sheets_service = sheets_service
    
    def check_conflicts(self, pilot_id: str, drone_id: str, project_id: str) -> dict:
        """
        Detect all conflicts for a proposed assignment.
        
        Returns:
            Dictionary with 'critical' and 'warnings' lists
        """
        critical = []  # Blockers - assignment cannot proceed
        warnings = []   # Need confirmation - assignment can proceed with approval
        
        try:
            # Get data
            pilots_df = self.sheets_service.get_pilots()
            drones_df = self.sheets_service.get_drones()
            missions_df = self.sheets_service.get_missions()
            
            # Find specific records
            pilot = pilots_df[pilots_df['pilot_id'] == pilot_id]
            drone = drones_df[drones_df['drone_id'] == drone_id]
            mission = missions_df[missions_df['project_id'] == project_id]
            
            if pilot.empty:
                return {'critical': [f"Pilot {pilot_id} not found"], 'warnings': []}
            if drone.empty:
                return {'critical': [f"Drone {drone_id} not found"], 'warnings': []}
            if mission.empty:
                return {'critical': [f"Project {project_id} not found"], 'warnings': []}
            
            pilot = pilot.iloc[0]
            drone = drone.iloc[0]
            mission = mission.iloc[0]
            
            # CRITICAL CONFLICTS (Blockers)
            
            # Pilot already assigned
            if pilot['status'] == 'Assigned' and pilot['current_assignment'] != '–':
                critical.append(f"🚫 Pilot {pilot_id} is already assigned to {pilot['current_assignment']}")
            
            # Pilot on leave
            if pilot['status'] == 'On Leave':
                critical.append(f"🚫 Pilot {pilot_id} is currently on leave until {pilot['available_from']}")
            
            # Skill mismatch
            required_skills = [s.strip() for s in str(mission['required_skills']).split(',')]
            pilot_skills = [s.strip() for s in str(pilot['skills']).split(',')]
            missing_skills = [skill for skill in required_skills if skill not in pilot_skills]
            if missing_skills:
                critical.append(f"🚫 Pilot {pilot_id} lacks required skills: {', '.join(missing_skills)}")
            
            # Certification mismatch
            if 'required_certs' in mission and mission['required_certs'] and mission['required_certs'] != '–':
                required_certs = [c.strip() for c in str(mission['required_certs']).split(',')]
                pilot_certs = [c.strip() for c in str(pilot['certifications']).split(',')]
                missing_certs = [cert for cert in required_certs if cert not in pilot_certs]
                if missing_certs:
                    critical.append(f"🚫 Pilot {pilot_id} lacks required certifications: {', '.join(missing_certs)}")
            
            # Drone in maintenance
            if drone['status'] == 'Maintenance':
                critical.append(f"🚫 Drone {drone_id} is currently in maintenance")
            
            # Drone already assigned
            if drone['status'] == 'Assigned' and drone['current_assignment'] != '–':
                critical.append(f"🚫 Drone {drone_id} is already assigned to {drone['current_assignment']}")
            
            # Date overlap check
            if pilot['current_assignment'] != '–' and pilot['current_assignment']:
                current_project = missions_df[missions_df['project_id'] == pilot['current_assignment']]
                if not current_project.empty:
                    overlaps = self._check_date_overlap(
                        current_project.iloc[0],
                        mission,
                        pilot_id
                    )
                    critical.extend([f"🚫 {conf}" for conf in overlaps])
            
            # Drone capability check
            required_capabilities = str(mission.get('required_skills', '')).lower()
            drone_capabilities = str(drone['capabilities']).lower()
            if 'thermal' in required_capabilities and 'thermal' not in drone_capabilities:
                critical.append(f"🚫 Drone {drone_id} does not have thermal capability required for this project")
            
            # WARNINGS (Need Confirmation)
            
            # Location mismatch (pilot and project) - WARNING, not blocker
            if pilot['location'] != mission['location']:
                warnings.append(
                    f"⚠️ Location mismatch: Pilot is in {pilot['location']}, Project is in {mission['location']}. "
                    f"Pilot will need to travel. Do you want to proceed with this assignment?"
                )
            
            # Location mismatch (pilot and drone) - WARNING
            if pilot['location'] != drone['location']:
                warnings.append(
                    f"⚠️ Drone location mismatch: Pilot is in {pilot['location']}, Drone is in {drone['location']}. "
                    f"Drone will need to be transported. Do you want to proceed?"
                )
            
            return {'critical': critical, 'warnings': warnings}
            
        except Exception as e:
            return {'critical': [f"Error checking conflicts: {str(e)}"], 'warnings': []}
    
    def _check_date_overlap(self, current_mission, new_mission, pilot_id) -> list:
        """Check if two missions have overlapping dates."""
        conflicts = []
        
        try:
            # Parse dates
            current_start = datetime.strptime(str(current_mission['start_date']), '%Y-%m-%d')
            current_end = datetime.strptime(str(current_mission['end_date']), '%Y-%m-%d')
            new_start = datetime.strptime(str(new_mission['start_date']), '%Y-%m-%d')
            new_end = datetime.strptime(str(new_mission['end_date']), '%Y-%m-%d')
            
            # Check for overlap
            if (new_start <= current_end) and (new_end >= current_start):
                conflicts.append(
                    f"Date conflict: Pilot {pilot_id} has overlapping assignment "
                    f"{current_mission['project_id']} ({current_start.date()} to {current_end.date()})"
                )
        except Exception as e:
            # If date parsing fails, skip date check
            pass
        
        return conflicts
    
    def find_urgent_reassignment_candidates(self, project_id: str) -> dict:
        """
        Find best candidates for urgent reassignment.
        
        Returns:
            Dictionary with available pilots and drones that match requirements.
        """
        try:
            missions_df = self.sheets_service.get_missions()
            pilots_df = self.sheets_service.get_pilots()
            drones_df = self.sheets_service.get_drones()
            
            mission = missions_df[missions_df['project_id'] == project_id]
            if mission.empty:
                return {"error": f"Project {project_id} not found"}
            
            mission = mission.iloc[0]
            
            # Find available pilots with matching skills
            available_pilots = pilots_df[pilots_df['status'] == 'Available']
            
            candidates = []
            for _, pilot in available_pilots.iterrows():
                # Check skill match
                required_skills = [s.strip() for s in str(mission['required_skills']).split(',')]
                pilot_skills = [s.strip() for s in str(pilot['skills']).split(',')]
                
                skill_matches = sum(1 for skill in required_skills if skill in pilot_skills)
                location_match = pilot['location'] == mission['location']
                
                # Find available drones in same location
                available_drones = drones_df[
                    (drones_df['status'] == 'Available') & 
                    (drones_df['location'] == pilot['location'])
                ]
                
                if not available_drones.empty:
                    candidates.append({
                        'pilot_id': pilot['pilot_id'],
                        'pilot_name': pilot['name'],
                        'drone_id': available_drones.iloc[0]['drone_id'],
                        'skill_match_score': skill_matches,
                        'location_match': location_match,
                        'total_score': skill_matches * 2 + (5 if location_match else 0)
                    })
            
            # Sort by score
            candidates.sort(key=lambda x: x['total_score'], reverse=True)
            
            return {
                'project_id': project_id,
                'candidates': candidates[:5]  # Top 5
            }
            
        except Exception as e:
            return {"error": f"Error finding candidates: {str(e)}"}

from langchain_core.tools import tool
import json
import pandas as pd
from typing import Optional


def create_tools(sheets_service, conflict_detector):
    """Create all tools with injected services."""
    
    @tool
    def query_pilots(skill: Optional[str] = None, location: Optional[str] = None, status: Optional[str] = None, certification: Optional[str] = None) -> str:
        """Query pilot roster based on skills, certifications, location, or status.
        
        Args:
            skill: Filter by skill (e.g., "Mapping", "Inspection")
            location: Filter by location (e.g., "Bangalore", "Mumbai")
            status: Filter by status (e.g., "Available", "On Leave", "Assigned")
            certification: Filter by certification (e.g., "DGCA", "Night Ops")
        """
        try:
            df = sheets_service.get_pilots()
            
            if skill:
                df = df[df['skills'].astype(str).str.contains(skill, case=False, na=False)]
            if location:
                df = df[df['location'].astype(str).str.contains(location, case=False, na=False)]
            if status:
                df = df[df['status'].astype(str).str.contains(status, case=False, na=False)]
            if certification:
                df = df[df['certifications'].astype(str).str.contains(certification, case=False, na=False)]
            
            return df.to_json(orient='records', indent=2) if not df.empty else "No pilots found matching criteria."
        except Exception as e:
            return f"Error: {str(e)}"
    
    @tool
    def update_pilot_status(pilot_id: str, status: str, available_from: Optional[str] = None, current_assignment: Optional[str] = None) -> str:
        """Update pilot status and sync to Google Sheets.
        
        Args:
            pilot_id: Pilot ID like P001
            status: New status (Available, On Leave, or Assigned)
            available_from: Date when pilot will be available (YYYY-MM-DD)
            current_assignment: Project ID if status is Assigned
        """
        try:
            success = sheets_service.update_pilot_status(pilot_id, status, available_from, current_assignment)
            return f"✅ Pilot {pilot_id} status updated to '{status}' and synced to Google Sheets." if success else f"❌ Failed to update pilot {pilot_id}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @tool
    def query_drones(capability: Optional[str] = None, location: Optional[str] = None, status: Optional[str] = None, model: Optional[str] = None) -> str:
        """Query drone fleet based on capabilities, status, location, or model.
        
        Args:
            capability: Filter by capability (e.g., "Thermal", "LiDAR", "RGB")
            location: Filter by location (e.g., "Bangalore", "Mumbai")
            status: Filter by status (e.g., "Available", "Maintenance", "Assigned")
            model: Filter by model (e.g., "DJI M300", "Mavic")
        """
        try:
            df = sheets_service.get_drones()
            
            if capability:
                df = df[df['capabilities'].astype(str).str.contains(capability, case=False, na=False)]
            if location:
                df = df[df['location'].astype(str).str.contains(location, case=False, na=False)]
            if status:
                df = df[df['status'].astype(str).str.contains(status, case=False, na=False)]
            if model:
                df = df[df['model'].astype(str).str.contains(model, case=False, na=False)]
            
            return df.to_json(orient='records', indent=2) if not df.empty else "No drones found matching criteria."
        except Exception as e:
            return f"Error: {str(e)}"
    
    @tool
    def update_drone_status(drone_id: str, status: str, current_assignment: Optional[str] = None) -> str:
        """Update drone status and sync to Google Sheets.
        
        Args:
            drone_id: Drone ID like D001
            status: New status (Available, Maintenance, or Assigned)
            current_assignment: Project ID if status is Assigned
        """
        try:
            success = sheets_service.update_drone_status(drone_id, status, current_assignment)
            return f"✅ Drone {drone_id} status updated to '{status}' and synced to Google Sheets." if success else f"❌ Failed to update drone {drone_id}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @tool
    def query_missions(priority: Optional[str] = None, location: Optional[str] = None, client: Optional[str] = None) -> str:
        """Query missions/projects based on priority, location, or client.
        
        Args:
            priority: Filter by priority (e.g., "Urgent", "High", "Standard")
            location: Filter by location (e.g., "Bangalore", "Mumbai")
            client: Filter by client name
        """
        try:
            df = sheets_service.get_missions()
            
            if priority:
                df = df[df['priority'].astype(str).str.contains(priority, case=False, na=False)]
            if location:
                df = df[df['location'].astype(str).str.contains(location, case=False, na=False)]
            if client:
                df = df[df['client'].astype(str).str.contains(client, case=False, na=False)]
            
            return df.to_json(orient='records', indent=2) if not df.empty else "No missions found matching criteria."
        except Exception as e:
            return f"Error: {str(e)}"
    
    @tool
    def detect_conflicts(pilot_id: str, drone_id: str, project_id: str) -> str:
        """Detect conflicts for a proposed assignment (pilot + drone + project).
        Checks: date overlaps, skill mismatches, location mismatches, drone maintenance status.
        Returns critical conflicts (blockers) and warnings (need confirmation).
        
        Args:
            pilot_id: Pilot ID like P001
            drone_id: Drone ID like D001
            project_id: Project ID like PRJ001
        """
        try:
            result = conflict_detector.check_conflicts(pilot_id, drone_id, project_id)
            
            critical = result.get('critical', [])
            warnings = result.get('warnings', [])
            
            if not critical and not warnings:
                return "✅ No conflicts detected. Assignment is safe to proceed."
            
            output = ""
            
            if critical:
                output += "🚫 CRITICAL CONFLICTS (Assignment CANNOT proceed):\n"
                for i, conflict in enumerate(critical, 1):
                    output += f"{i}. {conflict}\n"
            
            if warnings:
                if critical:
                    output += "\n"
                output += "⚠️ WARNINGS (Need user confirmation to proceed):\n"
                for i, warning in enumerate(warnings, 1):
                    output += f"{i}. {warning}\n"
                output += "\nIf user confirms, you can proceed with the assignment."
            
            return output
        except Exception as e:
            return f"Error: {str(e)}"
    
    @tool
    def match_pilot_to_project(project_id: str) -> str:
        """Find best available pilots for a project based on requirements.
        Returns pilots sorted by suitability (skill match, location match, availability).
        
        Args:
            project_id: Project ID like PRJ001
        """
        try:
            missions_df = sheets_service.get_missions()
            pilots_df = sheets_service.get_pilots()
            
            project = missions_df[missions_df['project_id'] == project_id]
            if project.empty:
                return f"Project {project_id} not found."
            
            project = project.iloc[0]
            required_skills = project['required_skills'].split(',')
            required_location = project['location']
            
            # Filter available pilots
            available_pilots = pilots_df[pilots_df['status'] == 'Available']
            
            # Score pilots
            matches = []
            for _, pilot in available_pilots.iterrows():
                score = 0
                pilot_skills = pilot['skills'].split(',')
                
                # Check skill match
                skill_match = any(req_skill.strip() in [ps.strip() for ps in pilot_skills] 
                                 for req_skill in required_skills)
                if skill_match:
                    score += 10
                
                # Check location match
                if pilot['location'] == required_location:
                    score += 5
                
                if score > 0:
                    matches.append({
                        'pilot_id': pilot['pilot_id'],
                        'name': pilot['name'],
                        'skills': pilot['skills'],
                        'location': pilot['location'],
                        'score': score
                    })
            
            if not matches:
                return f"No suitable pilots found for project {project_id}"
            
            # Sort by score
            matches.sort(key=lambda x: x['score'], reverse=True)
            return json.dumps(matches, indent=2)
            
        except Exception as e:
            return f"Error matching pilot to project: {str(e)}"

    return [
        query_pilots,
        update_pilot_status,
        query_drones,
        update_drone_status,
        query_missions,
        detect_conflicts,
        match_pilot_to_project,
    ]    



def get_all_tools(sheets_service, conflict_detector):
    """Get all tools for the agent."""
    return create_tools(sheets_service, conflict_detector)
import os
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st


class GoogleSheetsService:
    """Service for 2-way sync with Google Sheets."""
    
    def __init__(self):
        """Initialize Google Sheets client."""
        try:
            # Determine if running on Streamlit Cloud or locally
            running_on_cloud = False
            credentials = None
            
            # Try to access Streamlit secrets (only works on Streamlit Cloud)
            try:
                gcp_account = st.secrets["gcp_service_account"]
                running_on_cloud = True
                credentials = Credentials.from_service_account_info(
                    gcp_account,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                self.sheet_id = st.secrets["GOOGLE_SHEET_ID"]
                print("✅ Using Streamlit Cloud credentials")
            except (KeyError, FileNotFoundError):
                # Not on Streamlit Cloud, try local file
                running_on_cloud = False
            
            # Local development fallback
            if not running_on_cloud:
                scopes = ['https://www.googleapis.com/auth/spreadsheets']
                credentials = Credentials.from_service_account_file(
                    'config/service_account.json',
                    scopes=scopes
                )
                self.sheet_id = os.getenv("GOOGLE_SHEET_ID")
                print("✅ Using local credentials")
            
            # Authorize and connect
            self.client = gspread.authorize(credentials)
            self.spreadsheet = self.client.open_by_key(self.sheet_id)
            
            # Cache for data
            self._pilots_cache = None
            self._drones_cache = None
            self._missions_cache = None
            
        except Exception as e:
            raise Exception(f"Failed to initialize Google Sheets: {str(e)}")
    
    def get_pilots(self, refresh=False) -> pd.DataFrame:
        """Get pilot roster data from Google Sheets."""
        if self._pilots_cache is None or refresh:
            try:
                worksheet = self.spreadsheet.worksheet("Pilot Roster")
                data = worksheet.get_all_records()
                self._pilots_cache = pd.DataFrame(data)
            except Exception as e:
                # Fallback to local CSV if Google Sheets fails
                self._pilots_cache = pd.read_csv('pilot_roster.csv')
        return self._pilots_cache.copy()
    
    def get_drones(self, refresh=False) -> pd.DataFrame:
        """Get drone fleet data from Google Sheets."""
        if self._drones_cache is None or refresh:
            try:
                worksheet = self.spreadsheet.worksheet("Drone Fleet")
                data = worksheet.get_all_records()
                self._drones_cache = pd.DataFrame(data)
            except Exception as e:
                # Fallback to local CSV
                self._drones_cache = pd.read_csv('drone_fleet.csv')
        return self._drones_cache.copy()
    
    def get_missions(self, refresh=False) -> pd.DataFrame:
        """Get missions data from Google Sheets."""
        if self._missions_cache is None or refresh:
            try:
                worksheet = self.spreadsheet.worksheet("Missions")
                data = worksheet.get_all_records()
                self._missions_cache = pd.DataFrame(data)
            except Exception as e:
                # Fallback to local CSV
                self._missions_cache = pd.read_csv('missions.csv')
        return self._missions_cache.copy()
    
    def update_pilot_status(self, pilot_id: str, status: str, available_from: str = None, current_assignment: str = None) -> bool:
        """Update pilot status and sync back to Google Sheets."""
        try:
            worksheet = self.spreadsheet.worksheet("Pilot Roster")
            
            # Find the pilot row
            cell = worksheet.find(pilot_id)
            if not cell:
                return False
            
            row = cell.row
            
            # Update status (column 6)
            worksheet.update_cell(row, 6, status)
            
            # Update current_assignment (column 7)
            if current_assignment is not None:
                worksheet.update_cell(row, 7, current_assignment)
            elif status == "Available":
                worksheet.update_cell(row, 7, "–")
            
            # Update available_from (column 8)
            if available_from:
                worksheet.update_cell(row, 8, available_from)
            
            # Refresh cache
            self._pilots_cache = None
            return True
            
        except Exception as e:
            print(f"Error updating pilot status: {e}")
            return False
    
    def update_drone_status(self, drone_id: str, status: str, current_assignment: str = None) -> bool:
        """Update drone status and sync back to Google Sheets."""
        try:
            worksheet = self.spreadsheet.worksheet("Drone Fleet")
            
            # Find the drone row
            cell = worksheet.find(drone_id)
            if not cell:
                return False
            
            row = cell.row
            
            # Update status (column 4)
            worksheet.update_cell(row, 4, status)
            
            # Update current_assignment (column 6)
            if current_assignment is not None:
                worksheet.update_cell(row, 6, current_assignment)
            elif status == "Available":
                worksheet.update_cell(row, 6, "–")
            
            # Refresh cache
            self._drones_cache = None
            return True
            
        except Exception as e:
            print(f"Error updating drone status: {e}")
            return False
    
    def refresh_all(self):
        """Refresh all cached data."""
        self._pilots_cache = None
        self._drones_cache = None
        self._missions_cache = None

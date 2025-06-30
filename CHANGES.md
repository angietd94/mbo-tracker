# MBO Tracker Changes

## Bug Fixes

### 1. Fixed: Saving a new MBO as "Completed"
- Modified `add_mbo` function in `app/routes/mbo_routes.py` to respect the user-selected progress status instead of hardcoding "In progress"
- Now when a user selects "Finished" during creation, it will be saved correctly

### 2. Fixed: Moving MBOs to a different Quarter
- Enhanced `edit_mbo` function in `app/routes/mbo_routes.py` to process the creation date field
- Now when a user changes the date in the form, the MBO will be moved to the corresponding quarter

## Enhancements

### 3. Added: "Remember Me" checkbox to login
- Added a "Remember Me" checkbox to the login form in `app/templates/login.html`
- Modified the login function in `app/routes/auth_routes.py` to respect the "Remember Me" option
- When checked, the session will persist for a longer duration (30 days)

### 4. Added: Hide Admin user from dashboard
- Modified `dashboard_routes.py` to filter out admin users from the dashboard view
- Modified `user_routes.py` to hide admin users from the users list for non-admin users
- Modified `mbo_routes.py` to exclude admin users from the employee dropdown in team MBOs view
- Admin users are now hidden in all user-facing dashboards and dropdowns

### 5. Added: Spreadsheet download link in footer
- Created an MBO template spreadsheet at `app/static/templates/MBO_template.xlsx`
- Modified `app/templates/layout.html` to add a footer with a download link to the template
- The template includes example MBOs and proper formatting

### 6. Refactored: Harmonize MBO status labels
- Standardized on "Finished" instead of "Completed" in the MBO form
- Added a migration script `migrations/versions/standardize_mbo_status.py` to update any existing "Completed" statuses to "Finished"
- Ensured consistent labeling across the application

## How to Apply These Changes

1. Pull the latest code
2. Run database migrations: `flask db upgrade`
3. Restart the application: `./restart_app.sh`

## Testing

All changes have been tested to ensure they work as expected and don't break existing functionality.
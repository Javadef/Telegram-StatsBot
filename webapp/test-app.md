# Application Test Checklist

## Frontend Tests (http://localhost:3000)

### ✅ Layout & Navigation
- [ ] Dashboard page loads without errors
- [ ] Channels page loads without errors
- [ ] Sidebar navigation works
- [ ] Mobile responsive layout works

### ✅ Settings Menu
- [ ] Settings button visible in sidebar
- [ ] Theme picker (Primary & Neutral colors) works
- [ ] Appearance toggle (Light/Dark mode) works
- [ ] Language toggle (English/O'zbekcha) works
- [ ] Language changes persist on page reload

### ✅ Dashboard Page (Home)
- [ ] Shows channel selector when channels exist
- [ ] Shows "Add Channel" message when no channels
- [ ] Date range picker opens as popover
- [ ] Date range presets (7 days, 30 days, etc.) work
- [ ] Custom date selection works
- [ ] Calendar shows single month (mobile-friendly)
- [ ] Stats cards display data
- [ ] Views chart renders
- [ ] Engagement chart renders

### ✅ Channels Page
- [ ] Shows grid of channel cards
- [ ] Search filter works
- [ ] Type filter (All/Channel/Group/Private) works
- [ ] Click channel card opens details modal
- [ ] Modal shows complete channel info
- [ ] "Open Channel Link" button works (if username exists)
- [ ] Add Channel modal opens
- [ ] Date picker in Add Channel modal works

## Backend Tests (http://localhost:8000)

### ✅ API Endpoints
- [ ] GET /api/channels - Returns channel list
- [ ] GET /api/channels/{id} - Returns single channel
- [ ] GET /api/analytics?channel_id=X&start_date=Y&end_date=Z - Returns analytics
- [ ] GET /api/messages/{channel_id} - Returns messages
- [ ] POST /api/scrape_channel - Starts scraping
- [ ] GET /api/scrape_status - Returns scrape statuses

## Integration Tests

### ✅ Frontend ↔ Backend
- [ ] Dashboard fetches real channel data from backend
- [ ] Analytics updates when channel/date changes
- [ ] Channel list refreshes after adding new channel
- [ ] Scraping status updates in real-time
- [ ] Error messages display when backend is offline

## Bug Fixes Verified

### ✅ Issues Fixed
- [x] Language toggle now visible in settings menu
- [x] Channel selector doesn't ask to add channel when channels exist
- [x] Date picker is compact and mobile-friendly (1 calendar instead of 2)
- [x] Date range presets visible on mobile (horizontal scroll)
- [x] Custom date input works through calendar picker

## Testing Instructions

1. **Start Backend:**
   ```bash
   cd C:\Users\Java\Desktop\Telegram-StatsBot\bot
   venv\Scripts\activate
   python main.py
   ```

2. **Start Frontend:**
   ```bash
   cd C:\Users\Java\Desktop\Telegram-StatsBot\webapp
   pnpm dev
   ```

3. **Open Browser:**
   - Navigate to http://localhost:3000
   - Open DevTools Console (F12) to check for errors

4. **Test Language Toggle:**
   - Click Settings icon in sidebar
   - Click "Language" menu item
   - Select "O'zbekcha"
   - Verify UI text changes to Uzbek
   - Reload page - language should persist

5. **Test Dashboard:**
   - If no channels: Should show "Add Channel" message
   - If channels exist: Should show channel selector with first channel selected
   - Click date range picker - should open compact popover
   - Click preset ranges (Last 7 days, etc.)
   - Select custom dates from calendar

6. **Test Channels Page:**
   - Click "Channels" in sidebar
   - Verify cards display
   - Search for channel by name
   - Filter by type
   - Click card to view details
   - Click "Add Channel" button

## Expected Results

- ✅ No console errors
- ✅ All pages load successfully
- ✅ Language switching works smoothly
- ✅ Date picker is compact and easy to use
- ✅ Channel selection persists correctly
- ✅ Charts and stats display when data available

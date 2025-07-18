# 🍔 Responsive Hamburger Menu Feature

## Overview

The Responsive Hamburger Menu feature provides a mobile-friendly navigation experience with a collapsible sidebar menu. On desktop screens, the traditional horizontal navigation is maintained, while on mobile devices, a hamburger menu button reveals a stylish sidebar with all navigation options.

## Features

### 🎯 Core Functionality
- **Responsive Design**: Automatically switches between desktop and mobile navigation
- **Hamburger Menu**: Three-line menu button for mobile devices
- **Sidebar Navigation**: Collapsible offcanvas sidebar with organized sections
- **Smooth Animations**: Retro-themed transitions and hover effects
- **Auto-close**: Sidebar automatically closes when clicking navigation links on mobile

### 🎨 Visual Design
- **Retro Theme**: Consistent with the overall application aesthetic
- **Gradient Background**: Dark gradient background for the sidebar
- **Color-coded Sections**: Different sections for different navigation categories
- **Hover Effects**: Interactive hover animations with slide effects
- **Icon Integration**: Font Awesome icons for all navigation items

### 📱 Responsive Behavior

#### Desktop (≥992px)
- Traditional horizontal navigation bar
- All menu items visible in the header
- Hamburger menu button hidden
- Dropdown menus for user account

#### Mobile (<992px)
- Hamburger menu button visible
- Horizontal navigation hidden
- Sidebar slides in from the left
- Organized sections for better mobile UX

## Navigation Structure

### 🚀 Discover Section
- **Search Recipes**: Main recipe search functionality
- **Popular Recipes**: Trending and popular recipes

### 👤 My Account Section (Authenticated Users)
- **Dashboard**: User dashboard with personalized content
- **Favorites**: Saved favorite recipes
- **Collections**: User's recipe collections
- **Meal Plan**: Meal planning functionality
- **Preferences**: User preferences and settings

### 🔐 Account Section (Unauthenticated Users)
- **Login**: User authentication
- **Register**: New user registration

### 👤 User Profile Section (Authenticated Users)
- **Username Display**: Shows current user's username
- **Logout**: Secure logout functionality (highlighted in red)

## Technical Implementation

### HTML Structure
```html
<!-- Hamburger Menu Button -->
<button class="navbar-toggler hamburger-menu" data-bs-toggle="offcanvas" data-bs-target="#sidebarMenu">
    <span class="navbar-toggler-icon"></span>
</button>

<!-- Sidebar Menu -->
<div class="offcanvas offcanvas-start sidebar-menu" id="sidebarMenu">
    <div class="offcanvas-header">
        <h5 class="offcanvas-title">Menu</h5>
        <button class="btn-close btn-close-white" data-bs-dismiss="offcanvas"></button>
    </div>
    <div class="offcanvas-body">
        <!-- Navigation sections -->
    </div>
</div>
```

### CSS Features
- **Custom Hamburger Icon**: Retro-styled hamburger menu icon
- **Gradient Backgrounds**: Dark gradients for sidebar
- **Hover Animations**: Slide and color transitions
- **Responsive Breakpoints**: Bootstrap-compatible responsive design
- **Backdrop Blur**: Blurred background when sidebar is open

### JavaScript Enhancements
- **Auto-close Functionality**: Closes sidebar when clicking links on mobile
- **Hamburger Animation**: Rotation effect when clicking hamburger button
- **Hover Effects**: Dynamic hover animations for sidebar links
- **Responsive Detection**: Automatic behavior based on screen size

## CSS Classes

### Hamburger Menu
- `.hamburger-menu`: Main hamburger button styling
- `.hamburger-menu:hover`: Hover effects for the button
- `.hamburger-menu .navbar-toggler-icon`: Custom hamburger icon

### Sidebar Menu
- `.sidebar-menu`: Main sidebar container
- `.sidebar-menu .offcanvas-header`: Sidebar header styling
- `.sidebar-menu .offcanvas-title`: Sidebar title styling
- `.sidebar-nav`: Navigation container
- `.sidebar-section`: Individual navigation sections
- `.sidebar-section-title`: Section headers
- `.sidebar-link`: Navigation links
- `.sidebar-link:hover`: Link hover effects
- `.sidebar-link-danger`: Special styling for logout link

### Responsive Classes
- `.d-none.d-lg-flex`: Hides elements on mobile, shows on desktop
- `.offcanvas-backdrop`: Backdrop overlay styling

## Usage

### For Users
1. **Desktop**: Use the traditional horizontal navigation bar
2. **Mobile**: Tap the hamburger menu (☰) to open the sidebar
3. **Navigation**: Tap any menu item to navigate
4. **Close**: Tap the X button or outside the sidebar to close

### For Developers
1. The feature is automatically responsive
2. No additional configuration needed
3. Uses Bootstrap 5 offcanvas component
4. Customizable through CSS variables

## Browser Compatibility

- **Modern Browsers**: Full support for all features
- **Mobile Browsers**: Optimized for touch interactions
- **Progressive Enhancement**: Graceful degradation for older browsers

## Accessibility Features

- **ARIA Labels**: Proper accessibility labels for screen readers
- **Keyboard Navigation**: Full keyboard support
- **Focus Management**: Proper focus handling for sidebar
- **Screen Reader Support**: Semantic HTML structure

## Future Enhancements

- **Gesture Support**: Swipe gestures for mobile devices
- **Custom Animations**: More retro-themed animations
- **Theme Variations**: Different color schemes
- **Advanced Interactions**: Multi-level navigation support

## Files Modified

- `src/templates/base.html`: Updated navigation structure
- `src/static/css/style.css`: Added responsive menu styles
- `test_responsive_menu.html`: Test page for responsive behavior

## Testing

To test the responsive menu:
1. Open the application in a browser
2. Resize the window to test different screen sizes
3. On mobile size, click the hamburger menu
4. Test navigation links in the sidebar
5. Verify auto-close functionality

The hamburger menu provides an intuitive and visually appealing navigation experience that maintains the retro aesthetic while being fully responsive and accessible! 🍔✨ 
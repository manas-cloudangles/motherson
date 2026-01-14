# Angular Component Metadata

Total Components: 3

---

## 1. AppButtonComponent

**Description**: A reusable button component with customizable styling and behavior. Supports three visual variants (primary, secondary, danger) with hover effects and disabled states. Accepts inputs for label text, button type (button/submit/reset), disabled state, and variant style. Emits a 'clicked' event when the button is pressed (unless disabled). Should be used throughout the application wherever a styled button is needed, providing consistent UI and behavior.

**Import Path**: `app/common/components/app-button/app-button.component`

**ID/Selector**: `app-button`

---

## 2. AppFooterComponent

**Description**: A shared footer component that displays copyright information with the current year and a banner indicating it's a shared component. The footer has a dark blue background with white text, centered content, and is designed to stick to the bottom of the page layout. It automatically updates the copyright year based on the current date. This component should be used at the bottom of pages or in the main app layout to provide consistent footer styling across the application.

**Import Path**: `app/common/components/app-footer/app-footer.component`

**ID/Selector**: `app-footer`

---

## 3. AppHeaderComponent

**Description**: A navigation header component that displays the application title and provides dropdown navigation menus for different sections (Master, Logs). Features hover-activated dropdowns with route navigation, active link highlighting, and a shared component banner. Includes navigation items for Master components (5 items), Logs components (8 items), and displays a badge indicating shared component usage. Should be used as the main application header across all pages.

**Import Path**: `app/app-header/app-header.component`

**ID/Selector**: `app-header`

---


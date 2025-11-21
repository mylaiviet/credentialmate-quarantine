# **CredentialMate Design System Specification**
## **Version 1.0 — Foundations, Components, Tokens, Accessibility, and Frontend Consistency Rules**
### **Notes:**
This spec is optional but recommended. You may postpone full implementation, but this document serves as the authoritative blueprint.

### **Sources Incorporated:**
- Section 22 (UI/UX Architecture)
- Frontend stack: Next.js + Tailwind + Radix UI
- Notification & dashboard designs
- Developer stability rules (port locking, no FE drift)

---
# **1. PURPOSE OF THIS DOCUMENT**
The CredentialMate Design System provides a **unified visual + interaction standard** across all UIs:
- Provider Portal
- Admin Dashboard
- Notification Center
- Compliance Views
- Document Upload Flow

This ensures:
- Visual consistency
- Accessible, predictable components
- Easy onboarding of new developers
- Stable UI behavior across releases

---
# **2. DESIGN PRINCIPLES**
### **2.1 Clarity First**
UI must avoid cognitive load and show only what matters.

### **2.2 Minimum Necessary Visual Noise**
No unnecessary gradients, animations, or decorative UI.

### **2.3 Healthcare-Grade Accessibility (WCAG 2.1 AA)**
- Minimum 4.5:1 contrast
- Keyboard navigability
- Screen-reader labels

### **2.4 Deterministic UI**
Frontend rendering must:
- Use typed APIs only
- Never infer missing fields
- Never hide compliance severity

---
# **3. TOKENS & FOUNDATIONS**
### **3.1 Color Tokens**
```
--brand-primary: #0E7490;
--brand-secondary: #083344;
--brand-accent: #14B8A6;
--success: #22C55E;
--warning: #F59E0B;
--danger: #DC2626;
--text-primary: #0F172A;
--text-secondary: #475569;
--background: #FFFFFF;
--surface: #F8FAFC;
```

### **3.2 Typography Tokens**
- Inter (default)
- 14px → body
- 16px → body-strong
- 20px → section header
- 28px → page header

### **3.3 Spacing Tokens**
```
--space-1: 4px
--space-2: 8px
--space-3: 12px
--space-4: 16px
--space-6: 24px
--space-8: 32px
```

### **3.4 Radius Tokens**
```
--radius-sm: 4px
--radius-md: 8px
--radius-lg: 12px
--radius-xl: 20px
```

---
# **4. COMPONENT LIBRARY (RADIX + CUSTOM)**
### **4.1 Form Components**
- Text Input (Radix)
- Select (Radix)
- Picker: State, License Type
- Datepicker
- Upload Button → backed by pre-signed URL

### **4.2 Navigation Components**
- Top Nav (provider/admin variants)
- Sidebar (admin only)

### **4.3 Feedback Components**
- Toasts → success/warning/error
- Non-PHI error banners
- Inline form errors (422-safe)

### **4.4 Compliance Components**
- Compliance Status Card (color-coded)
- Gap List
- Timeline (cycle visualization)

### **4.5 Notification Center Components**
- Notification List Item
- Channel Preference Switches
- Quiet Hours Editor

---
# **5. LAYOUT SYSTEM**
### **5.1 Grid Rules**
- 12-column responsive grid
- 2-column split for dashboards

### **5.2 Page Templates**
- Auth Layout (minimal)
- Provider Dashboard Layout
- Admin Overview Layout

---
# **6. INTERACTION STANDARDS**
### **6.1 Button Behavior**
- Disable during async actions
- Show spinner for >400ms
- Never double-submit

### **6.2 Form Behavior**
- Autosave disabled (security)
- Explicit save required
- Inline validation

### **6.3 Loading States**
- Skeleton loaders
- No flashing content

### **6.4 Error States**
- Deterministic messaging
- No PHI in error messages

---
# **7. ACCESSIBILITY REQUIREMENTS (MANDATORY)**
### **7.1 Keyboard Navigation**
- All components focusable
- Skip-to-content link

### **7.2 ARIA Rules**
- Landmarks for nav, main, footer
- aria-describedby for forms

### **7.3 Screen Reader Messaging**
- Form errors must read automatically

---
# **8. BRANDING & IDENTITY RULES**
### **8.1 Logo Usage**
- Dark/light variants
- Min size 32px

### **8.2 Animation Rules**
- Subtle only
- No looping animations
- No distracting motion

### **8.3 Consistent Iconography**
- Lucide icons only
- 16px/20px variants

---
# **9. PERFORMANCE STANDARDS**
### **9.1 LCP Target**
< 2.5 seconds

### **9.2 Bundle Size Control**
- Code splitting required
- No large third-party components

### **9.3 Image Handling**
- Next/Image required
- Lazy loading

---
# **10. FE SECURITY RULES**
- No PHI persistence in localStorage
- No PHI in query params
- HTTPS required
- CSP enforced

---
# **11. FORBIDDEN UI ACTIONS**
- Never infer missing compliance data
- Never display partial or speculative records
- Never hide critical expiration statuses
- Never expose raw backend error traces
- Never use unapproved libraries

---
# **12. FUTURE EXTENSIONS**
- React Component Cookbook
- Figma component library
- Theming system for white-labeling

---
# **SUMMARY OF WHAT WAS ADDED (FOR COMPLETENESS)**
### ⭐ **1. Full token system (colors, typography, spacing, radius)**
### ⭐ **2. Component library definitions (Radix + custom CM components)**
### ⭐ **3. Layout + grid system**
### ⭐ **4. Interaction patterns (loading, forms, errors)**
### ⭐ **5. Mandatory accessibility rules (WCAG AA)**
### ⭐ **6. Performance standards (LCP, bundle size)**
### ⭐ **7. FE security rules (no PHI leakage)**
### ⭐ **8. Forbidden UI behaviors to ensure deterministic compliance**
### ⭐ **9. Future expansion roadmap (Figma, theming, cookbook)**

---
# **END OF DESIGN SYSTEM SPEC — VERSION 1.0**
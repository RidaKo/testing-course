## Test Case EC-03-1
id: EC-03-1  
title: Validate Progress Bar synchronization without fixed delays  
author: Ridas Kožukauskas  
target application: https://demoqa.com/progress-bar  
environment: Chromium (Playwright)  
test-type: UI automation test  
pre-conditions: DemoQA site is reachable  
post-conditions: Progress bar reset to 0  
pass_criteria: Progress bar can be started, stopped by condition, completed, and reset  
priority: High  
severity: Medium  

test_data:
  stop_threshold: 75

### Steps
1. Open `https://demoqa.com/progress-bar`.
2. Verify progress value is `0`.
3. Verify `Reset` button is not visible.
4. Click `Start`.
5. Wait until progress value is greater than or equal to `75`.
6. Click `Stop`.
7. Verify stopped progress value is `>= 75` and `< 100`.
8. Click `Start` again.
9. Verify progress value reaches `100`.
10. Verify `Reset` button becomes visible.
11. Click `Reset`.
12. Verify progress value returns to `0`.

## Test Case EC-03-2
id: EC-03-2  
title: Validate Dynamic Properties state changes  
author: Ridas Kožukauskas  
target application: https://demoqa.com/dynamic-properties  
environment: Chromium (Playwright)  
test-type: UI automation test  
pre-conditions: DemoQA site is reachable  
post-conditions: None  
pass_criteria: Delayed visibility/enabling and style change occur as expected  
priority: High  
severity: Medium  

test_data:
  max_wait_ms: 12000

### Steps
1. Open `https://demoqa.com/dynamic-properties`.
2. Verify `Will enable 5 seconds` button is disabled.
3. Capture initial CSS class list of `Color Change` button.
4. Wait until `Will enable 5 seconds` button becomes enabled.
5. Verify `Visible After 5 Seconds` button becomes visible.
6. Verify `Color Change` button class includes `text-danger`.
7. Verify class list changed from initial value.


## Test case attributes:
id: EC-01
title: Registered user adds multiple items (<$900) (> $9) to cart and proceeds through checkout
author: Ridas Kožukauskas
target application: https://demowebshop.tricentis.com/
environment: chromium(brave browser)
test-type: Ui-automation test 
pre-conditions: User is not logged in; site is available; test email not used before
selection-rule: Add multiple items where price > $9
post-conditions: User account exists; cart/order state saved depending on how far you proceed
pass_criteria: user completes his order successfully

test_data:
    price_range: (<$900) (> $9)
    email : lol123@lol.com
    password: lol123
    first_name: lol
    last_name: lol
    country: united_states
    postal_code: lol
    address_1: lol
    

## Steps
1. Open browser
2. Verify home page loads (top menu shows Register and Log in). 
3. Click Register. 
4. Select Gender (any). 
5. Enter First name and Last name. 
6. Enter a unique email. 
7. Enter Password and Confirm password. 
8. Click Register. 
9. Verify registration success message and/or user is logged in.
10. Click on the "Books" category
11. Click on add to cart button of all items that fit within price_range
12. Click on the "Computers" category
13. Click on the "Desktop" subcategory
14. Click on the Add to cart button of the items that fit within price_range
15. Click the add to cart button in the specific screen of the specific item
16. Click shopping cart link in the corner
17. Verify all added items are present in the cart. 
18. Verify each selected item is within range and cart subtotal reflects all items. 
19. In cart, change quantity of first item to 10 and click Update shopping cart. 
20. Verify totals/subtotal updated accordingly. 
21. Remove first item (tick “Remove”) and update cart. 
22. Verify the removed item no longer appears and totals adjust. 
23. Tick I agree with the terms of service. 
24. Click Checkout. 
25. If prompted, confirm/select billing address.
26. On Billing Address step, open the Billing address dropdown. 
27. Select New Address/ choose “New Address” option). 
28. Fill First name 
29. Fill Last name 
30. Fill Email
31. Select Country United States
32. For State / province, select Other. 
33. Fill City
34. Fill Address 1
35. Fill Zip / postal code
36. Fill Phone number. Click Continue to go to the next checkout step 
37. Select In Store-pickup checkbox. Click continue 
38. In payment method section click continue 
39. In payment info steps click continue.
40. On confirmation page, verify order summary includes the remaining expensive items and correct totals. Click Confirm

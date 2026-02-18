                                                          Organic Fruits and Vegetables Selling WebApp

	The Organic Fruits and Vegetables Selling WebApp is a web-based marketplace developed application using Django as the backend framework, HTML, CSS, and JavaScript used for the 
development of user interface, and MySQL as the database used here. The system is designed to directly connect organic farmers with customers, eliminating middlemen and ensuring fair 
pricing, transparency and trust. 
	Farmers can register on the platform, create profiles, upload product details with images, set prices, manage stock, and receive orders digitally. Customers can browse a wide range 
of fresh organic products, search and filter products, view farmer information( contact number and location ) and place secure online orders. The platform supports a customer feedback 
mechanism where users can submit ratings and reviews, that helping maintain product quality and credibility. To enhance the system’s effectiveness, several special features may include, 
such as farmer verification and organic certification validation, a freshness indicator based on harvest date, location-based product recommendations, secure order management, and an 
order tracking system.
These features are implemented using Django logic and interactive JavaScript functionality to ensure a seamless and user-friendly experience.

There are 3 modules occur:
1.	Farmer Module
  •	Farmer Registration & Verification
  •	Farmer Login
  •	Add Product (organic fruits,vegetables,diary..)
  •	Upload images with stoke count
  •	Set price, harvest date, Expiry date(to enhance freshness)
  •	Dashboard shows Total products added(verified by admin), Total Orders placed by Customers, Total revenue and low stock alerts if products count less than 5 kg.
  •  If admin reject any products added by farmers, it can shows in navbar of farmers dashboard with notification badge and can update and resend for admin aproval is possible.
  •	Order management

2.	Customer Module
•	User Registration/Login
•	Browse products/item on search bar and can filter products based on category on filter head.
•	Add products to Cart
•	Place Order(Quantity change is possible)
•	On checkout Online Payment / COD payment with promo code apply to get discount is possible and profile change(deleivery point) also possible. 
•	Track Order Status(orderd(pending to proceed), paid,shipped and delivered and cancelled also is possible to see.
•	Reviews & Ratings of customers shows in product card
•  If any product in productlist under low stock its add to cart button will disabled
•	products stock counts shows reduced in accordance wqith order placement
•	There is Farmers name also shown in product card.on click Farmers name it can redirect to farmers profile with contact and location

3.	Admin Module
•	Nav bar has notification alerts with pending item counts shown for Farmers verification pending count,Product verification pending count Order verification pending count,
  and payment confirmation pending count
•	Analytics Dashboard with Order Status Overview(Pending ,shipped,delivered and canceled), Daily Revenue (Last 7 Days) and also Monthly Revenue (Last 12 Months)
•	On Farmer verification (Approve/Reject farmers account, when admin add reason for reject and reject farmer. It will reflect 
	in farmers dashboard navbar as notification. After updation may reapply for approve is also possible) 
•	Approve/reject products in product approval page. if admin reject a product with reject reason enterd. It will reflect 
	in farmers dashboard navbar as notification. After updation may reapply for approve is also possible 
•	Manage users(Enable/Disable users account), orders(Status track control) and payments(monitor total revenue,paid amount, pending amount,succes transaction details.)

Overall, this application promotes sustainable agriculture, improves farmers’ market reach, and provides customers 
with easy access to authentic organic products through an efficient and transparent digital platform.
                     

# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/account/apikeys
stripe.api_key = "sk_test_YOUR_STRIPE_SECRET_KEY"

intent = stripe.PaymentIntent.create(
  amount=1099,
  currency='usd',
)

import type { FeedbackReviewInput } from "./types";

export const sampleReviewInput: FeedbackReviewInput = {
  product_name: "Compression leggings",
  product_category: "Women's activewear",
  product_description: "High-waist compression leggings for workouts, errands, and daily wear.",
  support_tickets: `- I'm between sizes. Should I size up or down?
- How long does shipping take?
- Are these squat-proof?
- Can I return them if they don't fit?
- Do they roll down at the waist?
- How do I wash them?
- I need to see this on different body types before buying.
- Has my order shipped yet?
- Does the waistband stay up during running?`,
  customer_reviews: `- Great fit but I wish the size guide was clearer.
- Shipping took longer than I expected.
- The waistband stayed up during workouts.
- I almost returned them because I ordered the wrong size.
- The material feels good but I wanted more fabric details before buying.
- Good leggings, but the product page did not explain washing instructions clearly.`,
  return_reasons: `- Ordered wrong size
- Expected thicker fabric
- Shipping took too long
- Did not know how compressed the fit would be`,
  social_comments: `- What size are you wearing?
- Are they see-through?
- Need to see this on short girls.
- Is this good for curvy girls?
- Can you show a squat test?
- What's your height and size?
- How long did shipping take?`,
  current_faq: "We offer returns within 30 days. Shipping varies by location.",
  product_page_copy:
    "Our compression leggings are comfortable, stylish, and perfect for workouts or everyday wear. Designed to move with you and support your active lifestyle.",
  main_business_concern:
    "Support keeps answering the same sizing and shipping questions, and UGC videos are not addressing buyer objections."
};

export const emptyReviewInput: FeedbackReviewInput = {
  product_name: "",
  product_category: "",
  product_description: "",
  support_tickets: "",
  customer_reviews: "",
  return_reasons: "",
  social_comments: "",
  current_faq: "",
  product_page_copy: "",
  main_business_concern: ""
};

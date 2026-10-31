from backend.app.services.missing_delivery import is_missing_delivery_issue

MISSING_DELIVERY_REPLY = (
    "We understand that your item is missing. Please check your order tracking "
    "for the latest delivery status. If the tracking shows that the order was "
    "delivered but you have not received it, please contact our support team "
    "so we can investigate the issue."
)


def draft_reply(
    ticket: str,
    category: str,
    knowledge_base: list
) -> str:
    if category == "Delivery" and is_missing_delivery_issue(ticket):
        return MISSING_DELIVERY_REPLY

    if not knowledge_base:
        return (
            "Thank you for contacting our support team. "
            "We have received your request and will review it shortly."
        )

    policy = knowledge_base[0]["content"]

    if category == "Payment":
        reply = (
            "We understand that there is an issue with your payment. "
            "We will first verify the transaction status. "
            "If the payment was successful but the order was not created, "
            "the payment will be reviewed for a refund according to our policy."
        )

    elif category == "Account":
        reply = (
            "We understand that you are having trouble with your account. "
            "If you forgot your password, please use the password reset option. "
            "For login issues, we will verify your registered email and account status."
        )

    elif category == "Delivery":
        reply = (
            "We understand that you are facing a delivery issue. "
            "Please check your order tracking information for the latest status. "
            "If your package is delayed or has not arrived within the expected "
            "delivery time, our delivery team can investigate the shipment."
        )

    elif category == "Refund":
        reply = (
            "We understand that you are requesting a refund. "
            "For damaged or broken products, we will verify the order and product condition. "
            "Eligible customers can request a refund or replacement according to our policy."
        )

    elif category == "Cancellation":
        reply = (
            "We understand that you want to cancel your order. "
            "Cancellation is generally possible before the order is shipped. "
            "If the order has already been shipped, cancellation may not be possible."
        )

    else:
        reply = (
            "Thank you for contacting our support team. "
            "We have received your request and will review it shortly."
        )

    return reply


if __name__ == "__main__":

    ticket = "My payment was deducted but my order is pending"

    knowledge_base = [
        {
            "name": "payment",
            "content": "Payment Support Policy"
        }
    ]

    reply = draft_reply(
        ticket,
        "Payment",
        knowledge_base
    )

    print("\n===== SUGGESTED REPLY =====")
    print(reply)
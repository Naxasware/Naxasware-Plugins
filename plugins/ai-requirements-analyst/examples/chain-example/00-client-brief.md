# Chain example: client brief (fictional)

Company: Acme Industrial Supplies (invented for this test).

"Our accounts-payable team (4 clerks and 1 AP manager) gets supplier invoices as PDF attachments in a shared mailbox.
The clerks re-type every invoice into our ERP. It is slow, typos happen, and we have paid the same invoice twice.

We want a system that reads the invoices, checks them against our purchase orders, and gets them approved faster.
Rules: nothing gets paid unless a person has approved it. The AI must never approve or pay anything.
Invoices above a certain amount need the AP manager, and very large ones need the Controller.
But small invoices should just go straight through without anyone looking at them, so the clerks are not bogged down.
We need a full audit trail. Our ERP has a REST API. The whole thing needs to be fast, accurate and secure.

We don't know yet how many invoices we get per month, what the amount thresholds are, or which ERP vendor we will be on."

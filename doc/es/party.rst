#:inside:party/party:bullet_list:campos_contabilidad#


* |customer_payment_days| y |supplier_payment_days|: nos permiten indicar los
  días del mes en que el tercero realiza los pagos y cobros. En caso de que el
  tercero pague mas de un día al mes, podemos especificar los días separados
  por espacios. Por ejemplo, si el cliente realiza pagos los días 5 y 20,
  deberemos introducir "5 20" para reflejarlo en el sistema. Con esa
  información el sistema es capaz de adaptar los vencimientos de las facturas
  para que concuerden con los días de pago definidos en el tercero.


.. |customer_payment_days| field:: party.party/customer_payment_days
.. |supplier_payment_days| field:: party.party/supplier_payment_days

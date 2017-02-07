\ Model transportation
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  - 30 prices[farm1] - 30 prices[farm2] + 20 prices[store1]
   + 20 prices[store2] + 20 prices[store3]
Subject To
 arbitrage[farm1,store1]: prices[farm1] - prices[store1] <= 100
 arbitrage[farm1,store2]: prices[farm1] - prices[store2] <= 80
 arbitrage[farm2,store1]: prices[farm2] - prices[store1] <= 120
 arbitrage[farm1,store3]: prices[farm1] - prices[store3] <= 120
 arbitrage[farm2,store3]: prices[farm2] - prices[store3] <= 120
 arbitrage[farm2,store2]: prices[farm2] - prices[store2] <= 120
Bounds
End

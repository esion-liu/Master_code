library("StatRank")

data(Data.Election1)

result <- Estimation.RUM.MLE(Data.Election1, iter = 10, dist = "norm")

print(result)
library("StatRank")
profile <- read.csv("/Users/yuchen/Documents/WorkSpace/R_WS/tie.csv")

result <- Estimation.RUM.MLE(profile, iter = 10, dist = "norm")

print(result)
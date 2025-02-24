library("StatRank")
profile <- read.csv("/Users/yuchen/Documents/WorkSpace/R_WS/gaussian_distorted_ballots.csv")

result <- Estimation.RUM.MLE(profile, iter = 10, dist = "norm")

print(result)
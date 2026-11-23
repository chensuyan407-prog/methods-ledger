# R version 4.3.1
library(drc)   # drc 3.0-1
set.seed(7)
dat <- read.csv("viability_summary.csv")
fit <- drm(mean_viability_pct ~ concentration_uM, data = dat, fct = LL.4())
ED(fit, 50, interval = "delta")
# one-way ANOVA vs vehicle with Dunnett post hoc
res <- aov(viability ~ factor(conc), data = raw)
alpha <- 0.05

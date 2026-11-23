# R version 4.3.2
library(mice)    # mice 3.16.0
library(lme4)    # lme4 1.1-35
set.seed(2023)
imp <- mice(dat, m = 20, seed = 2023)
fit <- with(imp, glmer(poor_sleep ~ gpa_low + grade + sex + (1 | college), family = binomial))
pool(fit)
alpha <- 0.05
# sensitivity: complete-case analysis

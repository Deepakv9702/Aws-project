# AWS FinOps — Cost Optimisation 

> **Real-world project** — mirrors the FinOps initiative led at Mercedes-Benz Financial Services USA. Achieved $180K/year savings (30% AWS cost reduction) through Savings Plans, EC2 auto-scheduling, and Aurora Serverless v2 migration.

## Outcomes
- **$180,000/year** AWS cost savings (30% reduction)
- 40+ idle resources decommissioned
- EC2 Compute Savings Plans: ~$70K/year saved
- Aurora Serverless v2 migration: ~$60K/year saved
- EC2 auto-scheduling (dev/staging): ~$50K/year saved

## Cost Saving Strategies
```
1. Savings Plans
   └── Compute Savings Plans (1-year, no-upfront)
       Savings: ~$70,000/year

2. Aurora Serverless v2 Migration
   └── dev/staging: from provisioned → serverless
       Savings: ~$60,000/year (scale-to-zero off-hours)

3. EC2 Auto-Scheduling
   └── dev/staging instances: stop at 7pm, start at 8am
       Savings: ~$50,000/year (14hrs/day off)

4. Idle Resource Cleanup
   └── 40+ unattached EBS volumes, old snapshots, unused EIPs
       Savings: one-time $20,000 + ongoing

5. Right-sizing
   └── Oversized EC2 instances → smaller families
       Savings: ~$10,000/year
```

## Author
**Deepak Vaida** | [LinkedIn](https://www.linkedin.com/in/deepak-vaida-0a66a12a5/)

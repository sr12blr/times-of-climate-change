# SEO Plan for Times of Climate Change

A comprehensive, prioritized plan to make the site more search-friendly. Work through these tiers at your own pace.

---

## 🎯 Tier 1: Quick Wins (Do These First)

### 1. Meta Tags & Descriptions ⭐ High Impact
Add unique meta descriptions to every story page (155-160 characters each).

**Example:**
```html
<meta name="description" content="Why India's water crisis matters to you: food prices rising, health impacts, and what you can do about it.">
```

**Where to add:** In story template HTML head
**Impact:** Improves click-through rate (CTR) from search results
**Time:** 30 mins for all stories

---

### 2. Structured Data (Schema.org) ⭐ High Impact
Add JSON-LD NewsArticle schema to help Google understand story content better.

**Template:**
```json
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "Story Title",
  "description": "Short description",
  "image": "image-url",
  "datePublished": "2026-03-31",
  "dateModified": "2026-03-31",
  "author": {
    "@type": "Organization",
    "name": "The Times of Climate Change"
  },
  "publisher": {
    "@type": "Organization",
    "name": "The Times of Climate Change",
    "logo": "logo-url"
  },
  "articleBody": "Full story text here"
}
```

**Where to add:** In story template, inside `<script type="application/ld+json">`
**Impact:** Enables rich snippets, improves ranking
**Time:** 1 hour to implement in template

---

### 3. Internal Linking ⭐ High Impact
Link related stories contextually within story text and in sidebar.

**Strategy:**
- Use "More Threads to Tug On" sidebar (already doing this!)
- Add contextual links in story body to related stories
- Link category pages from story content (e.g., link to explore/food when mentioning food prices)

**Example:**
```html
Read more about <a href="/story/climate-change-bangalore-filter-coffee-expensive/">
how climate change affects coffee prices</a> across India.
```

**Impact:** Distributes page authority, helps navigation, improves SEO
**Time:** Ongoing with each new story

---

### 4. Optimize Page Titles ⭐ Medium Impact
Improve HTML `<title>` tags with keywords and brand name.

**Current approach (probably):** "Story Title"

**Better approach:** "Story Title | Climate News India" or "Story Title - How Climate Change Affects Food Prices"

**Guidelines:**
- 50-60 characters
- Include primary keyword
- Include brand name
- Make it compelling for clicks

**Example:**
- ❌ Bad: "Water Crisis"
- ✅ Good: "India's Water Crisis: Why Food Prices Are Rising - Climate News"

**Time:** 30 mins across all stories

---

## 🎯 Tier 2: Moderate Effort, High Value

### 5. Open Graph Tags (Social Sharing) ⭐ Medium Impact
Improve how stories look when shared on social media (Facebook, Twitter, WhatsApp, LinkedIn).

**Template:**
```html
<meta property="og:title" content="Story Title">
<meta property="og:description" content="Brief description">
<meta property="og:image" content="https://timesofclimatechange.com/image.jpg">
<meta property="og:url" content="https://timesofclimatechange.com/story/slug/">
<meta property="og:type" content="article">
<meta property="article:published_time" content="2026-03-31T00:00:00Z">
<meta property="article:author" content="The Times of Climate Change">
```

**Also add Twitter Card tags:**
```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Story Title">
<meta name="twitter:description" content="Description">
<meta name="twitter:image" content="image-url">
```

**Impact:** Better engagement when shared, increased referral traffic
**Time:** 1 hour to implement

---

### 6. Image Optimization ⭐ Medium Impact

**For all story images:**

1. **Alt Text** (required for accessibility & SEO)
   ```html
   <img src="image.jpg" alt="Flamingo birds in toxic Navi Mumbai lake with industrial pollution">
   ```

2. **Descriptive Filenames**
   ```
   ❌ Bad: image1.jpg, photo.jpg
   ✅ Good: flamingo-lake-toxic-water-navi-mumbai.jpg
   ```

3. **Image Compression**
   - Use tools like TinyPNG, ImageOptim
   - Target: < 100KB per image
   - Faster loading = better SEO

4. **Image Title Attribute**
   ```html
   <img ... title="Flamingo birds affected by toxic lake pollution">
   ```

**Impact:** Images rank in image search, faster page load
**Time:** 1 hour for existing images

---

### 7. Page Speed Optimization ⭐ Medium Impact

**Test your site:**
- Google PageSpeed Insights: https://pagespeed.web.dev
- Mobile-Friendly Test: https://search.google.com/test/mobile-friendly

**Quick wins:**
1. Lazy load images (load only when scrolled into view)
2. Minify CSS/JavaScript
3. Remove unused styles
4. Enable Gzip compression (usually on by default with Vercel)

**For images specifically:**
- Use modern formats (WebP with fallback)
- Consider CDN for image delivery (Cloudinary free tier)

**Impact:** Faster sites rank better, better user experience
**Time:** 2-3 hours depending on issues found

---

### 8. Mobile Responsiveness ⭐ Medium Impact

**Test:**
- Google Mobile-Friendly Test
- Use Chrome DevTools to test on mobile sizes

**Checklist:**
- [ ] Buttons/links are clickable on mobile (48px+ size)
- [ ] Text is readable (no tiny fonts)
- [ ] Images scale properly
- [ ] No horizontal scrolling
- [ ] Touch-friendly spacing

**Impact:** Mobile is ~50% of traffic now, critical for ranking
**Time:** Testing only (you mentioned responsive design already)

---

## 🎯 Tier 3: Content Strategy

### 9. Target Long-Tail Keywords ⭐ High Impact
Your stories are already doing this well! Examples:
- "climate change food prices India"
- "water shortage Maharashtra farming"
- "heat impact health India monsoon"
- "air pollution Delhi children health"

**Make sure these phrases appear in:**
- Page title (H1)
- Meta description
- First 100 words of story
- Subheadings (H2, H3)
- Image alt text

**How to find keywords:**
- Google Suggest (start typing in search bar)
- Google Trends
- Answer the Public (answerthepublic.com)
- AnswerThePublic shows common questions about topics

**Time:** Integrate into each new story

---

### 10. Category Pages Optimization ⭐ Medium Impact

**For pages like `/explore/food/`, `/explore/water/`, etc:**

Add to each category page:
1. **Clear Description** — What's this category about?
2. **All Stories List** — Show all stories in that category
3. **Meta Description** — Unique, keyword-rich (155-160 chars)
4. **Page Title** — "Climate & Food Prices India" not just "Food"
5. **Structured Data** — CollectionPage schema

**Example for Food category:**
```
Title: "Climate Change & Food Prices in India | Times of Climate Change"
Description: "How climate change is affecting food prices, agricultural yields, and your daily expenses in India. Read stories about weather, crops, and food security."
```

**Impact:** Category pages can rank for competitive keywords
**Time:** 1-2 hours for all category pages

---

### 11. Create FAQ Section (Optional) ⭐ Low Priority
FAQ pages help with search and answer user questions.

**Example FAQs:**
- "How does climate change affect food prices in India?"
- "What is the relationship between heat and health?"
- "Why is water scarcity worsening in India?"
- "How does air pollution affect children in cities?"

**Format with Schema.org FAQPage:**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How does climate change affect food prices?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "..."
      }
    }
  ]
}
```

**Impact:** Can trigger FAQ rich snippets in search results
**Time:** 2-3 hours

---

### 12. Write Better Subtitles/Summaries ⭐ High Impact
Your subtitle field is already great! It improves:
- Click-through rate (CTR) in search results
- User engagement
- Keyword coverage

**Example subtitle patterns:**
- "How [issue] is affecting [location/group] and what you can do"
- "Why [phenomenon] matters to your [wallet/health/daily life]"
- "[Action] is driving [change]: here's what's happening"

**Time:** Ongoing with each story

---

## 🎯 Tier 4: Authority & Backlinks

### 13. Get Backlinks ⭐ High Impact (Long-term)

**Strategy:**
- Share stories with Indian climate/environment blogs
- Pitch stories to news aggregators
- Contact environmental NGOs and mention your coverage
- Reach out to journalists who might link to your research
- Submit best stories to news directories

**Tools:**
- BuzzSumo (find who's sharing similar topics)
- Ahrefs (see competitor backlinks)

**Impact:** Backlinks are huge ranking factor
**Time:** Ongoing, 30 mins per outreach

---

### 14. XML Sitemap ✅ Already Done!
You've completed this step. Google now knows about all your pages.

---

### 15. Submit to Google News (Optional but Powerful) ⭐ Medium Impact

**If you want news search visibility:**

1. Go to Google Search Console
2. Click "News" in left sidebar
3. Click "Google News publisher center"
4. Verify you're a news organization (minimum requirements: regular publishing schedule)
5. Submit your site

**Eligibility:**
- Original, timely content (you have this!)
- Regular publishing schedule (1 story/day, perfect!)
- Clear authorship (add author tags)
- Quality writing (you're doing this)

**Benefit:** Appear in Google News results, reach news-seeking audience

**Time:** 30 mins to set up

---

## 📊 Implementation Priority Matrix

| Task | Time | Impact | Difficulty | Do First? |
|------|------|--------|------------|-----------|
| Meta descriptions | 30 min | ⭐⭐⭐ | Easy | ✅ YES |
| Structured data (Schema) | 1 hour | ⭐⭐⭐ | Medium | ✅ YES |
| Internal linking | 30 min | ⭐⭐⭐ | Easy | ✅ YES |
| Page title optimization | 30 min | ⭐⭐ | Easy | ✅ YES |
| Open Graph tags | 1 hour | ⭐⭐ | Easy | ✅ YES |
| Image optimization | 1 hour | ⭐⭐ | Medium | Later |
| Page speed check | 1 hour | ⭐⭐ | Medium | Later |
| Category page SEO | 2 hours | ⭐⭐ | Medium | Later |
| FAQ section | 3 hours | ⭐ | Medium | Optional |
| Backlink outreach | Ongoing | ⭐⭐⭐ | Hard | Later |
| Google News submit | 30 min | ⭐⭐ | Easy | Later |

---

## 🚀 Recommended Implementation Timeline

### Week 1: Foundation (2-3 hours)
- [ ] Add meta descriptions to all stories
- [ ] Add basic page title optimization
- [ ] Add Open Graph tags to templates

### Week 2: Structured Data (1-2 hours)
- [ ] Implement NewsArticle schema in story template
- [ ] Test schema with Google's Rich Result Tester

### Week 3: Content & Internal Links (1 hour)
- [ ] Audit and improve internal linking
- [ ] Optimize category pages

### Week 4+: Ongoing
- [ ] Optimize images as you add them
- [ ] Run PageSpeed tests
- [ ] Start backlink outreach
- [ ] Monitor rankings in Google Search Console

---

## 🔍 Tools to Use (Free)

1. **Google Search Console** (essential)
   - Monitor what Google knows about your site
   - See search impressions and clicks

2. **Google PageSpeed Insights**
   - Test page speed and get recommendations

3. **Google Mobile-Friendly Test**
   - Test mobile responsiveness

4. **Schema.org Markup Validator**
   - Validate structured data
   - https://validator.schema.org

5. **Google Rich Results Tester**
   - Test if your schema produces rich snippets

6. **Ubersuggest** (free tier)
   - Find keywords and see search volume

7. **AnswerThePublic**
   - See common questions people ask about topics

---

## 📈 How to Measure Success

**Track in Google Search Console:**
- Impressions (how often your site appears in search results)
- Clicks (how many people click through)
- Average position (where you rank)
- Click-through rate (CTR)

**Set goals:**
- Week 1: Get domain indexed (you have this!)
- Month 1: 100+ search impressions/day
- Month 3: 10+ clicks/day
- Month 6: Top 10 rankings for target keywords

**Note:** SEO takes time (3-6 months to see major changes). Be patient!

---

## ✅ Checklist - What's Already Done

- [x] Sitemap created and submitted to Google
- [x] Robots.txt created
- [x] Domain verified in Google Search Console
- [x] Responsive design ✅
- [x] Clean URL structure (good slugs)
- [x] Good content (daily stories, unique angle)
- [x] Category pages exist

## ⚠️ Next Priority: Meta Descriptions & Structured Data

These two things will give you the best bang for your buck in the short term.

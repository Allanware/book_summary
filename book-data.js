const BOOK_DATA = {
  title: "Empire of Cotton",
  coreArgument:
    "From premodern household cotton worlds—often spun by women and traded as currency—to today’s retailer-led supply chains, the book argues cotton repeatedly reorganized labor, land, and state power to build modern capitalism. European “war capitalism” (chartered companies, armed trade, colonial seizure, and slavery) redirected cotton into Atlantic circuits and pushed plantation frontiers to supply mechanized mills. Industrial capitalism then scaled the system through factory discipline and merchant-finance hubs that standardized grades, prices, credit, and information; after the U.S. Civil War’s cotton famine, empires rebuilt supply through colonial law, infrastructure, and coercive rural credit regimes. In the twentieth and twenty-first centuries, production and manufacturing shifted toward Asia and other low-wage regions, while states still subsidize growers and police labor—so coercion persists alongside dramatic productivity gains.",
  themes: [
    {
      id: "labor-regimes",
      label: "Labor Regimes",
      description:
        "How cotton organized work in households, plantations, and factories.",
      definition:
        "Systems that mobilize cotton labor across time and place—household spinning and weaving, enslaved plantation gangs, factory wage labor, and coerced tenancy or colonial work—organized by households, planters, employers, and states through gendered roles, contracts, surveillance, and violence.",
      applications: [
        {
          chapter: 1,
          setting: "Pacific-coast villages in the Aztec Empire",
          time: "1518",
          point:
            "Household labor and tribute obligations organized cotton work, with villagers processing cotton by hand for elite payments.",
          evidence: [
            "In 1518, twelve Pacific-coast villages delivered 800 bales plus thousands of cloths to Moctezuma II as annual tribute. (p. 24)",
            "Villagers processed cotton by hand from seed removal through spinning and backstrap-loom weaving inside their huts. (p. 24)"
          ]
        },
        {
          chapter: 2,
          setting: "Gold Coast and Atlantic plantation zones",
          time: "1500s-1700s",
          point:
            "Atlantic plantation labor was secured through slave trading in which textiles bought captives, producing massive forced migration.",
          evidence: [
            "European powers built coastal forts and over 8 million Africans were transported to the Americas after 1500. (p. 58-59)",
            "In Richard Miles's 1772-1780 barters on the Gold Coast, textiles made up more than half the value used to buy enslaved people. (p. 59)"
          ]
        },
        {
          chapter: 3,
          setting: "Manchester-Lancashire mills (Quarry Bank)",
          time: "1780s-1830s",
          point:
            "Factory labor regimes centralized production and relied on women and children working for wages, including poorhouse apprentices.",
          evidence: [
            "In 1784 Samuel Greg gathered children from poorhouses to work alongside water frames at Quarry Bank Mill. (p. 82-83)",
            "The chapter notes that most mill workers were women and children and that most labor was waged. (p. 98)"
          ]
        },
        {
          chapter: 4,
          setting: "Saint-Domingue and Caribbean cotton frontier",
          time: "1780s-1791",
          point:
            "Caribbean cotton expansion depended on enslaved labor mobilized through violent supervision for effort-intensive plantation work.",
          evidence: [
            "In 1791 Saint-Domingue exported 6.8 million pounds of cotton while importing about a quarter million enslaved Africans between 1784 and 1791. (p. 121)",
            "The chapter ties cotton's rise to slavery-enabled rapid labor mobilization and violent supervision for an effort-intensive crop. (p. 121)"
          ]
        },
        {
          chapter: 5,
          setting: "U.S. Deep South plantations",
          time: "1790s-1860",
          point:
            "The U.S. cotton boom relied on slave markets and forced migration that concentrated enslaved labor on large plantations.",
          evidence: [
            "Declining tobacco profits in the upper South pushed enslaved people south; by 1830 about 1 million people grew cotton, most of them enslaved. (p. 144)",
            "The internal slave trade ultimately moved up to a million enslaved people to the Deep South to grow cotton. (p. 144)"
          ]
        },
        {
          chapter: 7,
          setting: "Lancashire and European mills",
          time: "1830s-1850s",
          point:
            "Industrial cotton depended on child-heavy, long-hour factory labor enforced through harsh discipline.",
          evidence: [
            "In 1833, 10-year-old Ellen Hootton reported 14.5-hour days and beatings at Eccles Spinning Mill. (p. 223-224)",
            "In 1833, 36 percent of Lancashire cotton workers were under 16. (p. 240)"
          ]
        },
        {
          chapter: 9,
          setting: "Manchester and Liverpool cotton circles",
          time: "1860s Civil War",
          point:
            "After emancipation threatened slave labor, manufacturers argued that disciplined labor was the key constraint and sought new coercive systems.",
          evidence: [
            "The Manchester Cotton Supply Association argued that land and climate were abundant but labor was the first requisite. (p. 336)",
            "The Economist called for organized labor under European supervision to replace slavery's coercive order. (p. 337-338)"
          ]
        },
        {
          chapter: 10,
          setting: "Mississippi Delta plantations",
          time: "1867-1900",
          point:
            "Sharecropping and high-interest credit locked freedpeople into cotton production under a new labor regime.",
          evidence: [
            "Sharecropping spread rapidly; by 1900 more than three-quarters of Black farmers in multiple Deep South states were croppers or renters. (p. 352)",
            "On Mississippi's Runnymede plantation, croppers paid 25 percent interest for food and 35 percent for clothing. (p. 353)"
          ]
        },
        {
          chapter: 12,
          setting: "German Togo and Belgian Congo",
          time: "1911-1914",
          point:
            "Colonial cotton schemes enforced labor through mandatory cultivation, controlled buying stations, and corporal punishment.",
          evidence: [
            "By 1911-1914 German Togo used authorized buying stations and corporal punishment while relying on forced labor for cotton handling and roads. (p. 457-458)",
            "In the Belgian Congo cotton became a mandatory culture obligatoire enforced with penalties and whippings. (p. 459)"
          ]
        },
        {
          chapter: 13,
          setting: "Japanese spinning mills",
          time: "1890s-1930s",
          point:
            "Japan's export surge rested on a low-wage female labor regime with long shifts and dormitory control.",
          evidence: [
            "In 1897, 79 percent of workers were female and 15 percent were under fourteen, often in twelve-hour two-shift systems. (p. 498-499)",
            "Factory protections were delayed until 1920 as Japan expanded cloth exports. (p. 499-500)"
          ]
        },
        {
          chapter: 14,
          setting: "Uzbekistan and India cotton farming",
          time: "2000s",
          point:
            "Modern cotton farming still uses coercion and debt, from forced cultivation to crisis-driven farmer suicides.",
          evidence: [
            "Uzbekistan forces farmers to grow cotton, and Tajik farmers incur debt through costly GMO seed systems. (p. 530)",
            "In India, a 2005 season of weak rains led hundreds of indebted cotton farmers to commit suicide. (p. 530)"
          ]
        }
      ]
    },
    {
      id: "state-power",
      label: "State Power",
      description:
        "Laws, coercion, and infrastructure that reshaped cotton.",
      definition:
        "State institutions (chartered companies, colonial administrations, and national governments) used law, coercion, infrastructure, and protectionism to seize land, discipline labor, and structure cotton markets across empires and nations.",
      applications: [
        {
          chapter: 2,
          setting: "Bengal under East India Company rule",
          time: "1765-1790s",
          point:
            "Company territorial rule imposed exclusive contracts and coercive inspections to control weaving in Bengal.",
          evidence: [
            "After 1765 the East India Company ruled Bengal and sought to force weavers into exclusive supply. (p. 67-68)",
            "Weavers were inspected on the loom and punished for selling elsewhere; agents used flogging and public humiliation. (p. 69)"
          ]
        },
        {
          chapter: 3,
          setting: "Britain",
          time: "1786-1830s",
          point:
            "The British state protected industrial advantage by banning machine exports and enforcing trade and contract protections that sustained exports.",
          evidence: [
            "The state banned textile machine exports after 1786 to protect British advantage. (p. 96)",
            "Export growth depended on the navy, bills of lading, and contract enforcement, with legislative protection. (p. 106-107)"
          ]
        },
        {
          chapter: 4,
          setting: "British Caribbean colonies",
          time: "1768-1780s",
          point:
            "British institutions used tariffs and incentives to push plantation cotton expansion, linking state policy to second-slavery frontiers.",
          evidence: [
            "The Royal Society of Arts offered a gold medal (1768) and Britain levied a tariff on cotton imported on foreign boats (1780). (p. 122)",
            "Colonial governors promised incentives including free land for cotton cultivation. (p. 122)"
          ]
        },
        {
          chapter: 6,
          setting: "Continental Europe and the United States",
          time: "1806-1840s",
          point:
            "States launched mechanized cotton by subsidies, blockades, and tariffs that created protected markets for new mills.",
          evidence: [
            "French, Saxon, Russian, and Danish governments issued loans, subsidies, or monopolies to early mills. (p. 199-200)",
            "The continental blockade and U.S. embargo protected markets, with U.S. spindles rising from 8,000 in 1807 to 130,000 by 1815. (p. 200-202)"
          ]
        },
        {
          chapter: 7,
          setting: "Britain and Prussia",
          time: "1823-1845",
          point:
            "States enforced factory wage labor through criminal penalties for contract breach.",
          evidence: [
            "Britain's 1823 Master and Servant Act allowed imprisonment for breach, with about 10,000 prosecutions per year in 1857-1875. (p. 230)",
            "Prussia's 1845 Gewerbeordnung imposed fines and prison for workers who left jobs without permission. (p. 231)"
          ]
        },
        {
          chapter: 8,
          setting: "British India and Liverpool merchant lobbying",
          time: "1850s-1870s",
          point:
            "Merchant lobbying translated into state-built infrastructure and formal cotton-market rules in colonial India.",
          evidence: [
            "Merchants lobbied for docks, storage, railways, waterways, and enforceable commercial law to speed trade. (p. 296)",
            "British cotton legislation in India formalized market rules at the intersection of merchant lobbying and state power. (p. 297)"
          ]
        },
        {
          chapter: 9,
          setting: "Confederate States and Union blockade",
          time: "1861-1863",
          point:
            "War-state actions (export embargo and blockade) collapsed cotton exports and made supply a legislative security issue.",
          evidence: [
            "Exports to Europe fell from 3.8 million bales in 1860 to virtually none by 1862 after the Confederate embargo and Union blockade. (p. 308)",
            "Cotton was debated in British and French legislatures; Palmerston argued England must have cotton to prevent mass suffering. (p. 312-313)"
          ]
        },
        {
          chapter: 10,
          setting: "Berar, colonial India",
          time: "1853-1880s",
          point:
            "Colonial rule remade land and infrastructure to turn Berar into an export cotton monoculture.",
          evidence: [
            "Britain assumed control of Berar in 1853 and completed the Khamgaon railroad in 1870, linking cotton to Bombay and Europe. (p. 363-364)",
            "Cotton acreage in Berar doubled from 1861 to 1865 and doubled again by the 1880s. (p. 367)"
          ]
        },
        {
          chapter: 11,
          setting: "Ottoman Empire and China",
          time: "1838-1900",
          point:
            "Imperial treaties and colonial tariffs opened markets to European cloth and dismantled local textile industries.",
          evidence: [
            "The 1838 imposition of free trade on the Ottoman Empire and the 1842 Treaty of Nanking opened markets to European cloth with devastating effects on local producers. (p. 400)",
            "Colonial governments imposed tariffs and excise duties against indigenous producers and built infrastructure for global market access. (p. 402)"
          ]
        },
        {
          chapter: 12,
          setting: "Korea under Japanese colonial rule",
          time: "1904-1920",
          point:
            "Japanese colonial authorities used directives, credit institutions, and seed programs to redirect Korean farming toward cotton exports.",
          evidence: [
            "After 1904 the Association for the Cultivation of Cotton in Korea introduced American strains and built a gin, and in 1906 the Korean Cotton Corporation loaned against mortgaged crops. (p. 420)",
            "After the 1910 occupation, the Governor-General ordered upland cotton planting and exports to Japan jumped to 165 million pounds by 1916-20. (p. 421)"
          ]
        }
      ]
    },
    {
      id: "market-infrastructure",
      label: "Market Infrastructure",
      description:
        "Trade, finance, and standards that connected cotton globally.",
      definition:
        "Merchant and financial systems that connect cotton across distance—trade routes, credit and factoring, exchanges and grading standards, price information, and retailer-led supply chains—linking growers, manufacturers, and consumers.",
      applications: [
        {
          chapter: 1,
          setting: "Indian Ocean trade routes",
          time: "first millennium CE-1500s",
          point:
            "Cotton cloth functioned as currency and moved through Indian Ocean trade networks linking India to Africa and Southeast Asia.",
          evidence: [
            "Cotton cloth functioned as tax payment and currency across China, Africa, Southeast Asia, and Mesoamerica. (p. 37)",
            "Indian cotton moved by dhows, caravans, and junks to Egypt, the Middle East, East Africa, and Southeast Asia. (p. 39)"
          ]
        },
        {
          chapter: 5,
          setting: "Charleston, Memphis, New Orleans, and Liverpool",
          time: "1820s-1850s",
          point:
            "Transatlantic merchant networks and slave-mortgage credit integrated U.S. cotton exports with European finance.",
          evidence: [
            "European import merchants stationed agents in Charleston, Memphis, and New Orleans and built dense shipping connections. (p. 149)",
            "In Louisiana 88 percent of loans and in South Carolina 82 percent used enslaved people as collateral. (p. 150)"
          ]
        },
        {
          chapter: 6,
          setting: "Chemnitz and Swiss putting-out regions",
          time: "1790s-1830s",
          point:
            "Merchants advanced raw cotton and coordinated household spinning through putting-out networks before shifting workers into factories.",
          evidence: [
            "Around Chemnitz, merchants advanced raw cotton and by 1799 about 15,000 people spun in their homes. (p. 182-183)",
            "In Switzerland, merchants shifted spinners into factories as they brought wage workers into mechanized mills. (p. 183-184)"
          ]
        },
        {
          chapter: 8,
          setting: "Liverpool Cotton Exchange",
          time: "1809-1860s",
          point:
            "Liverpool's exchange and brokers standardized grades and prices, creating a global signal system for cotton.",
          evidence: [
            "Liverpool price quotations were tracked from Bombay to the U.S. South and guided investment decisions. (p. 255)",
            "Brokers introduced buying by sample and grade categories that standardized cotton for machine production. (p. 264-265)"
          ]
        },
        {
          chapter: 11,
          setting: "Global cotton exchanges",
          time: "1869-1910s",
          point:
            "Exchanges and futures trading standardized cotton and produced a single world price accessible everywhere.",
          evidence: [
            "Cotton exchanges spread globally after 1869, enabled by telegraphy and standardized grades. (p. 394)",
            "Futures volumes soon dwarfed physical harvests and produced a single world price. (p. 396)"
          ]
        },
        {
          chapter: 13,
          setting: "Ahmedabad",
          time: "1860s-1918",
          point:
            "Merchant capital from long-distance trade and moneylending was reinvested into mills, building Ahmedabad's industrial cluster.",
          evidence: [
            "Ahmedabad merchants long dominated cotton trade and finance and shifted into manufacturing in the 1870s. (p. 467)",
            "Shapur Mill expanded quickly from 2,500 spindles to 10,000 by 1865, showing trade capital reinvested in industry. (p. 466)"
          ]
        },
        {
          chapter: 14,
          setting: "Global apparel supply chains",
          time: "late 20th century-present",
          point:
            "Retailers coordinate multi-country supply chains that link growers, spinners, and garment factories across the global South.",
          evidence: [
            "A typical shirt could be grown in China, India, Uzbekistan, or Senegal, spun in China, Turkey, or Pakistan, and sewn in Bangladesh or Vietnam. (p. 526-527)",
            "About 98 percent of garments sold in the United States are made abroad. (p. 528)"
          ]
        }
      ]
    }
  ],
  flow: [
    {
      id: "premodern-origins",
      title: "Premodern Cotton Worlds",
      summary:
        "From roughly 5000 BCE through the 1500s, cotton was a household crop and textile in South Asia, Africa, and the Americas, with Indian cloth serving as a regional currency and long-distance trade good long before European dominance.",
      mechanism: "Household cultivation, gendered spinning, and regional exchange",
      period: "5000 BCE-1500s",
      chapters: [1],
      themes: ["labor-regimes", "market-infrastructure"],
      thesisLinks: [
        {
          chapter: 1,
          point:
            "Household growers and weavers domesticated cotton across South Asia, Africa, and the Americas, while Indian cloth circulated as currency and long-distance trade goods.",
          evidence: [
            "Indus Valley sites show cotton textiles dated 3250-2750 BCE and cottonseeds at Mehrgarh dated to 5000 BCE. (p. 28)",
            "Cotton cloth functioned as tax payments and currency across regions, and Indian cotton moved by dhows and caravans to Africa, the Middle East, and Southeast Asia. (p. 37-39)"
          ]
        }
      ]
    },
    {
      id: "war-capitalism",
      title: "War Capitalism and Atlantic Cotton",
      summary:
        "European states and chartered companies used armed trade and colonial conquest to redirect Indian textiles into Atlantic circuits that purchased enslaved Africans, while British mechanization demanded ever more raw cotton and pushed plantation frontiers and the U.S. slave-cotton boom.",
      mechanism: "State-backed violence, slavery, and commodity frontiers",
      period: "late 1400s-1850s",
      chapters: [2, 3, 4, 5],
      themes: ["labor-regimes", "state-power", "market-infrastructure"],
      thesisLinks: [
        {
          chapter: 2,
          point:
            "Chartered companies and European naval power redirected Indian textiles into Atlantic trade and used cotton cloth as the main currency for enslaved labor.",
          evidence: [
            "By 1766 cotton cloth made up more than 75 percent of the East India Company’s exports. (p. 56)",
            "In Richard Miles’s 1772-1780 barters, textiles accounted for more than half the value used to purchase enslaved people on the Gold Coast. (p. 59)"
          ]
        },
        {
          chapter: 3,
          point:
            "British mechanization concentrated spinning in mills tied to Atlantic slave-grown cotton and slashed production costs.",
          evidence: [
            "Samuel Greg’s Quarry Bank Mill (1784) drew cotton from Caribbean sources supplied through Liverpool merchants. (p. 82-84)",
            "Spinning 100 pounds of cotton fell from 50,000 hours in India to 1,000 hours in Britain by 1790, and to 135 hours after 1825. (p. 94-95)"
          ]
        },
        {
          chapter: 4,
          point:
            "Industrial demand fueled a ‘second slavery’ across Caribbean and South American cotton frontiers built on land seizure and enslaved labor.",
          evidence: [
            "Cotton imports from British-controlled islands quadrupled between 1781 and 1791, and French Saint-Domingue exports doubled in the same decade. (p. 119)",
            "The chapter reports that 46 percent of enslaved people sold to the Americas arrived after 1780 as cotton frontiers expanded. (p. 123)"
          ]
        },
        {
          chapter: 5,
          point:
            "The U.S. cotton boom combined technological change, land seizure, and forced migration to make the United States the dominant supplier.",
          evidence: [
            "Whitney’s 1793 gin increased ginning productivity about fiftyfold and triggered a cotton rush into the interior. (p. 136)",
            "U.S. cotton production jumped from 1.5 million pounds (1790) to 36.5 million (1800) and 167.5 million (1820), and the internal slave trade relocated up to a million people to the Deep South. (p. 138, p. 144)"
          ]
        }
      ]
    },
    {
      id: "industrial-integration",
      title: "Industrial Capitalism and Global Integration",
      summary:
        "Mechanized mills diffused across Europe and the Americas under tariff protection and state support, factory regimes mobilized wage labor through legal coercion and discipline, and Liverpool-based merchants standardized grades, credit, and information to coordinate a global cotton chain.",
      mechanism: "Mechanization, wage-labor discipline, and merchant-finance networks",
      period: "1780s-1860s",
      chapters: [6, 7, 8],
      themes: ["labor-regimes", "state-power", "market-infrastructure"],
      thesisLinks: [
        {
          chapter: 6,
          point:
            "Mechanized mills spread quickly beyond Britain, often protected by tariffs and state policy that nurtured new industrial centers.",
          evidence: [
            "By 1860 mills operated across Europe, North America, India, Mexico, and Brazil, though Britain still held 67.4 percent of global spindles. (p. 178)",
            "The continental blockade and U.S. embargoes spurred mill growth, with U.S. spindles rising from 8,000 (1807) to 130,000 (1815). (p. 200-202)"
          ]
        },
        {
          chapter: 7,
          point:
            "Factory labor was mobilized through coercive legal regimes, child labor, and punishing hours.",
          evidence: [
            "In 1833, child worker Ellen Hootton reported 14.5-hour days and beatings in a Manchester-area mill. (p. 223-224)",
            "Britain’s 1823 Master and Servant Act enabled imprisonment for contract breaches, with roughly 10,000 prosecutions per year by 1857-1875. (p. 230)"
          ]
        },
        {
          chapter: 8,
          point:
            "Liverpool’s exchange and merchant system standardized grades and prices, letting merchants coordinate global cotton flows.",
          evidence: [
            "Liverpool price quotations guided decisions from Bombay to Mississippi, making the port the cotton empire’s command node. (p. 254-255)",
            "Brokers introduced buying by sample and grade categories that standardized cotton for machine production. (p. 264-265)"
          ]
        }
      ]
    },
    {
      id: "civil-war-reordering",
      title: "Cotton Famine and Imperial Reordering",
      summary:
        "The U.S. Civil War severed slave-cotton supply and created a global cotton famine, pushing states and manufacturers to rebuild supply through colonial law, infrastructure, and new labor regimes, while imperial integration and standardized exchanges undermined older textile economies.",
      mechanism: "War disruption, state reconstruction, and imperial market-making",
      period: "1860s-1910s",
      chapters: [9, 10, 11],
      themes: ["labor-regimes", "state-power", "market-infrastructure"],
      thesisLinks: [
        {
          chapter: 9,
          point:
            "The Confederate export embargo and Union blockade collapsed cotton exports and forced states to seek new supplies abroad.",
          evidence: [
            "Exports to Europe fell from 3.8 million bales in 1860 to virtually none by 1862, triggering the cotton famine. (p. 308)",
            "India’s share of Britain’s supply jumped from 16 percent (1860) to 75 percent (1862) as new sources were mobilized. (p. 318-319)"
          ]
        },
        {
          chapter: 10,
          point:
            "Post-emancipation reconstruction imposed coercive labor regimes and credit systems that restored U.S. dominance while colonial states reshaped cotton regions.",
          evidence: [
            "Sharecropping spread rapidly; by 1900 more than three-quarters of Black farmers in multiple Deep South states were croppers or renters. (p. 352)",
            "U.S. output surpassed its 1860 high by 1870 and by 1891 supplied 81 percent of the British market. (p. 360)"
          ]
        },
        {
          chapter: 11,
          point:
            "Imperial integration standardized cotton markets and deindustrialized older textile regions.",
          evidence: [
            "Cotton exchanges and futures trading spread globally after 1869, creating standardized grades and a single world price. (p. 394-396)",
            "Britain’s share of the Indian market rose to about 60 percent by 1880 as colonial policy built markets for metropolitan textiles. (p. 405)"
          ]
        }
      ]
    },
    {
      id: "new-imperialism-south",
      title: "New Cotton Imperialism and Southern Industrialization",
      summary:
        "Around 1900, imperial states launched new cotton programs in Korea, Central Asia, and Africa to secure raw materials, while manufacturing leadership shifted toward Asia and other low-wage regions through tariffs, state planning, and nationalist mobilization.",
      mechanism: "Colonial cotton programs, cost competition, and nationalist industrialization",
      period: "1900s-1930s (into mid-century)",
      chapters: [12, 13],
      themes: ["labor-regimes", "state-power", "market-infrastructure"],
      thesisLinks: [
        {
          chapter: 12,
          point:
            "Imperial states responded to price shocks with coercive cotton programs, using colonial infrastructure and labor controls to expand supply.",
          evidence: [
            "Cotton prices rose 121 percent between 1898 and 1913, fueling a renewed imperial cotton rush. (p. 424-425)",
            "In German Togo, colonial authorities imposed supervised buying stations and corporal punishment to enforce cotton production. (p. 457-458)"
          ]
        },
        {
          chapter: 13,
          point:
            "Manufacturing leadership shifted toward Asia as Britain declined and Japan, India, and China rapidly expanded spindles and exports.",
          evidence: [
            "Britain’s share of world mechanical spindles fell from 61 percent (1860) to 34 percent (1930), while Japan and China expanded rapidly. (p. 468-469)",
            "By 1933 Japan exported more cloth than Britain, France, and Germany, reaching 37 percent of global cloth exports by 1937. (p. 499-500)"
          ]
        }
      ]
    },
    {
      id: "contemporary-empire",
      title: "Retailer-Led Global Cotton Empire",
      summary:
        "After mid-century, cotton production and manufacturing re-centered in Asia and the global South, large retailers orchestrated global supply chains, and states continued to subsidize growers and police labor, sustaining coercion alongside rising productivity.",
      mechanism: "Global supply chains, state subsidies, and capital mobility",
      period: "1950s-2010s",
      chapters: [14],
      themes: ["labor-regimes", "market-infrastructure"],
      thesisLinks: [
        {
          chapter: 14,
          point:
            "The late-twentieth-century cotton empire shifted decisively to Asia and the global South while retailers and states shaped a globalized chain.",
          evidence: [
            "By the late 1960s the U.K. held only 2.8 percent of global cotton cloth exports, while today 98 percent of U.S. garments are made abroad. (p. 526, p. 528)",
            "Retailers like Walmart and Carrefour ‘pull’ products across global supply chains, coordinating contractors and suppliers. (p. 532)"
          ]
        },
        {
          chapter: 14,
          point:
            "States still underpin cotton through subsidies and labor coercion even as capital mobility intensifies inequality and a race to the bottom.",
          evidence: [
            "In 2001 the U.S. paid $4 billion in cotton subsidies and the EU subsidized cotton at 160-189 percent of world prices. (p. 538-539)",
            "Walmart and other retailers continually move production to lower-wage countries, deepening the race to the bottom. (p. 541)"
          ]
        },
        {
          chapter: 14,
          point:
            "Productivity gains are dramatic despite persistent coercion, suggesting the possibility of a more just cotton economy.",
          evidence: [
            "In 1950s northern China it took about sixty days of labor to clothe a family, while a U.S. family today spends about 3.4 percent of income on clothing. (p. 543)",
            "The chapter anticipates cotton production could triple or quadruple by 2050. (p. 543-544)"
          ]
        }
      ]
    }
  ]
};

export default BOOK_DATA;

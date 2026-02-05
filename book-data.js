const BOOK_DATA = {
  title: "Empire of Cotton",
  coreArgument:
    "From premodern household cotton worlds—often spun by women and traded as currency—to today’s retailer-led supply chains, the book argues cotton repeatedly reorganized labor, land, and state power to build modern capitalism. European “war capitalism” (chartered companies, armed trade, colonial seizure, and slavery) redirected cotton into Atlantic circuits and pushed plantation frontiers to supply mechanized mills. Industrial capitalism then scaled the system through factory discipline and merchant-finance hubs that standardized grades, prices, credit, and information; after the U.S. Civil War’s cotton famine, empires rebuilt supply through colonial law, infrastructure, and coercive rural credit regimes. In the twentieth and twenty-first centuries, production and manufacturing shifted toward Asia and other low-wage regions, while states still subsidize growers and police labor—so coercion persists alongside dramatic productivity gains.",
  themes: [
    {
      id: "placeholder",
      label: "Placeholder",
      description: "Placeholder keyword for UI testing.",
      definition:
        "A placeholder definition that names actors, mechanisms, and scope for layout testing.",
      applications: [
        {
          chapter: 1,
          setting: "Test setting: coastal villages",
          time: "1500s",
          point:
            "Placeholder application shows how the keyword appears in a specific context.",
          evidence: [
            "Placeholder evidence example with page citation. (p. 12)",
            "Second placeholder evidence detail for layout. (p. 13)"
          ]
        },
        {
          chapter: 5,
          setting: "Test setting: port city exchange",
          time: "1800s",
          point:
            "Second application demonstrates multiple entries across chapters.",
          evidence: ["Additional placeholder evidence. (p. 99)"]
        }
      ]
    },
    {
      id: "placeholder-2",
      label: "Placeholder Two",
      description: "Second placeholder keyword for UI testing.",
      definition:
        "Another placeholder definition used to verify keyword card switching.",
      applications: [
        {
          chapter: 2,
          setting: "Test setting: river delta market",
          time: "1600s",
          point:
            "Second placeholder application shows switching between keyword cards.",
          evidence: [
            "Placeholder evidence for the second keyword. (p. 21)"
          ]
        },
        {
          chapter: 8,
          setting: "Test setting: merchant exchange",
          time: "1800s",
          point:
            "A second application verifies multi-entry rendering in the card.",
          evidence: [
            "Additional placeholder evidence for layout. (p. 201)"
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

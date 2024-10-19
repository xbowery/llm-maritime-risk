import re
from datasketch import MinHash, MinHashLSH
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Helper function to get trigrams from text
def get_trigrams(text):
    text = re.sub(r'\W+', '', text.lower())  # Remove non-alphanumeric characters and lowercase the text
    return [text[i:i+3] for i in range(len(text) - 2)]

# Generate MinHash signature
def minhash_signature(trigrams, num_perm=128):
    m = MinHash(num_perm=num_perm)
    for trigram in trigrams:
        m.update(trigram.encode('utf8'))
    return m

load_dotenv()
documents = [
"""
The FBI said Friday that a bullet or fragments of it struck Donald Trump's ear during an assassination attempt on the former president this month at a campaign rally.
“What struck former President Trump in the ear was a bullet, whether whole or fragmented into smaller pieces, fired from the deceased subject's rifle," the FBI said in a statement.
The statement comes two days after FBI Director Christopher Wray, whom Trump nominated to his post in 2017, told House lawmakers that "there's some question about whether or not it's a bullet or shrapnel that, you know, hit his ear."
Wray had testified about the FBI's ongoing probe into the assassination attempt. A gunman identified as Thomas Crooks, 20, was shot and killed after opening fire from an elevated post not far from Trump's July 13 rally in Butler, Pennsylvania, that left one spectator dead and two others critically injured.
The director's remarks before a House committee sparked widespread backlash among Republican lawmakers, as well as Trump, who has consistently said he was hit by a bullet.
The former president has not released any medical records from his treatment at the hospital after the shooting. His campaign previously released a July 20 letter from Rep. Ronny Jackson, R-Texas, a former White House physician, who said that he had evaluated and treated Trump’s wound “daily” since the shooting and that Trump had "sustained a gunshot wound to the right ear."
Trump referred to the new FBI statement in a social media post Friday night.
"I assume that's the best apology that we'll get from Director Wray, but it is fully accepted!," he wrote on Truth Social.
House Speaker Mike Johnson had also criticized Wray's testimony.
“We've all seen the video, we've seen the analysis, we've heard it from multiple sources in different angles that a bullet went through his ear. I’m not sure it matters that much,” Johnson said on Thursday.
Wray's testimony came the same day the House approved a resolution to create a bipartisan task force to examine the assassination attempt.
Before the FBI put out its statement Friday night, Sen. Lindsey Graham, R-S.C., had written a letter to Wray urging him to revise his testimony, saying, "the attempted assassin’s bullet ripped the upper part" of Trump's ear, and that it "should not be a point of contention."
Graham said Friday night, after the FBI's statement, that Wray should never have suggested otherwise.
"Glad the FBI confirmed what everyone else knew. It was a bullet that struck President Trump. The statement by the FBI Director should’ve never been made," Graham wrote on X.
""",
"""
Former United States President Donald Trump has been shot in the ear during a campaign rally in an attack that drew condemnation from leading Republicans and Democrats and is being investigated as an assassination attempt.
The shooting on Saturday streaked blood across Trump’s face and set off panic among the thousands of people attending the rally in the city of Butler in Pennsylvania.
Trump's campaign said the Republican presidential candidate was “doing well” after the shooting, which the former leader said pierced the upper part of his right ear. At least one spectator was killed and two others were critically wounded, according to authorities.
The Secret Service said it shot the suspected assailant dead.

The shooting took place after Trump, 78, just started his speech. The former president grabbed his right ear with his right hand, then brought his hand down to look at it before dropping to his knees behind the podium. Secret Service agents then swarmed Trump, before he emerged and pumped his fist in the air, appearing to mouth the words “Fight! Fight! Fight!”
He was later whisked from the stage and ushered into a vehicle.
“I was shot with a bullet that pierced the upper part of my right ear,” Trump said on his Truth Social platform following the shooting. “Much bleeding took place.”
The FBI called the attack an “assassination attempt” and said it had taken the lead in investigating the case.
Kevin Rojek, a spokesman for the agency, said officials have identified the shooter, but would not release details. He added that a motive was not immediately clear.
The attack was the most serious assassination attempt on a US president or presidential candidate since Ronald Reagan was shot in 1981. It came in a deeply polarised political atmosphere, just four months from the presidential elections and days before Trump is to be officially named the Republican nominee at his party's convention - which his campaign said would proceed as planned.
'It felt like an assassination attempt'
US President Joe Biden was quick to condemn the attack.
“There's no place in America for this type of violence,” Biden, who is running against Trump as the presumptive Democratic nominee, said in remarks. “It's sick. It's sick.”
Ron Moose, a Trump supporter who was at the rally, described the chaos: “I heard about four shots and I saw the crowd go down and then Trump ducked also real quick. Then the Secret Service all jumped and protected him as soon as they could. We are talking within a second they were all protecting him.”
Moose said he then saw a man running and being chased by officers in military uniforms. He said he heard additional shots but was unsure who fired them. He noted that by then, snipers had set up on the roof of a warehouse behind the stage.
The shots appeared to come from outside the area secured by the Secret Service, the agency said.
Republican US Senate candidate David McCormick, who was seated in the front row at the rally, said he had started to go up on stage when Trump said he would have him come up later.
“Within a minute or two, I heard the shots … It was clear it was gunfire,” he told the Reuters news agency. “It felt like it was an assassination attempt … It was terrifying.”
The attack drew condemnation from leaders from both sides of the political aisle.
“This horrific act of political violence at a peaceful campaign rally has no place in this country and should be unanimously and forcefully condemned,” Republican House of Representatives Speaker Mike Johnson said on social media.
Democratic Senate Majority Leader Chuck Schumer said he was horrified by what happened and relieved Trump was safe.
“Political violence has no place in our country,” he said.
Some of Trump's Republican allies said they believed the attack was politically motivated.
“For weeks, Democrat leaders have been fuelling ludicrous hysteria that Donald Trump winning re-election would be the end of democracy in America,” said US Representative Steve Scalise, the No 2 House Republican who survived a politically-motivated shooting in 2017.
"""
]
# Create LSH index with threshold
lsh = MinHashLSH(threshold=0.1, num_perm=128)

# Add documents to LSH index
minhashes = {}  # Store MinHash signatures for later use
# read = set()
for i, doc in enumerate(documents):
    # if i >= 1000:
    #     break
    trigrams = get_trigrams(doc)
    m = minhash_signature(trigrams)
    # if doc['headline'] in read:
    #     print(f">>>> problem! {doc}")
    #     continue
    lsh.insert(f"{doc}", m)
    minhashes[f"{doc}"] = m  # Store the signature for comparison
    # read.add(doc)

# Querying for similar documents
for i, doc in enumerate(documents):
    query_doc = f"{doc}"
    query_trigrams = get_trigrams(query_doc)
    query_minhash = minhash_signature(query_trigrams)
    similar_docs = lsh.query(query_minhash)

    for doc_another in similar_docs:
        if doc_another == doc:
            continue
        sim_percentage = query_minhash.jaccard(minhashes[doc_another]) * 100
        print(f"Document 1'{doc}' and Document 2 '{doc_another}': {sim_percentage:.2f}%")

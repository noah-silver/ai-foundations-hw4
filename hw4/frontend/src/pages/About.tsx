const milestones = [
  { year: '1872', text: 'Blue first takes the field against Columbia, and New Haven learns to love a Saturday.' },
  { year: '1914', text: 'The Bowl opens its gates, and the town grows a second heartbeat on game days.' },
  { year: 'Today', text: 'Campus Customs keeps the tradition stitched into every crest, cuff, and collar.' },
]

export default function About() {
  return (
    <>
      <section className="page-head">
        <div className="container">
          <p className="eyebrow light">About Us</p>
          <h1>Outfitters to the Bulldog faithful.</h1>
        </div>
      </section>

      <section className="container section about">
        <div className="about-copy">
          <p className="lede">
            We started with a simple idea: the people who pack the Bowl every fall deserve clothing as good as the
            tradition they're cheering for.
          </p>
          <p>
            Campus Customs is a New Haven shop run by people who plan their autumns around the football schedule. We
            stock heritage sweatshirts, residential college crests, and sideline-ready layers for students, alumni,
            and every proud parent, grandparent, and uncle in the section.
          </p>
          <p>
            Our taste runs classic: navy and white, sturdy knits, and emblems placed with restraint. Our goal is that
            anything you buy here still earns a compliment at your twenty-fifth reunion.
          </p>
          <p>
            Every piece in our lineup is chosen for comfort in a cold grandstand, durability through a dozen seasons of
            tailgates, and a look that fits as well in a lecture hall as it does on the Old Campus lawn.
          </p>
        </div>
        <aside className="timeline">
          <p className="eyebrow">A Short History</p>
          {milestones.map((m) => (
            <div key={m.year} className="milestone">
              <span>{m.year}</span>
              <p>{m.text}</p>
            </div>
          ))}
        </aside>
      </section>
    </>
  )
}

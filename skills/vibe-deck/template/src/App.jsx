import { config } from './theme'
import Deck from './components/Deck'
import Slide from './components/Slide'
import PasswordGateComponent from './components/PasswordGate'
import SlideCover from './slides/SlideCover'

const Wrapper = config.password ? PasswordGateComponent : ({ children }) => children

export default function App() {
  return (
    <Wrapper>
      <Deck>
        <Slide title="Cover"><SlideCover /></Slide>
      </Deck>
    </Wrapper>
  )
}

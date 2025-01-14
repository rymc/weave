import {LegacyWBIcon} from '@wandb/weave/common/components/elements/LegacyWBIcon';
import {Icon, Modal} from 'semantic-ui-react';
import styled, {css, keyframes} from 'styled-components';

interface ControlWrapperProps {
  hovering: boolean;
  canFullscreen?: boolean;
}
export const ControlWrapper = styled.div<ControlWrapperProps>`
  position: relative;
  width: 100%;
  height: 100%;
  /* ${({hovering}) => css`
    border: ${hovering ? '1px solid #eee' : 'none'};
    padding: ${hovering ? '0px' : '1px'};
  `} */
`;

interface ControlWrapperBarProps {
  hovering: boolean;
}
export const ControlWrapperBar = styled.div<ControlWrapperBarProps>`
  position: absolute;
  visibility: ${props => (props.hovering ? 'visible' : 'hidden')};
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
`;

interface ControlWrapperContentProps {
  canFullscreen?: boolean;
}

export const ControlWrapperContent = styled.div<ControlWrapperContentProps>`
  height: 100%;
  ${({canFullscreen}) =>
    canFullscreen &&
    css`
      overflow: hidden;
    `}
`;

export const IconButton = styled.span`
  width: 22px;
  height: 20px;
  color: #3b3f42;
  background-color: #b3b3b3;
  margin-left: 5px;
  margin-top: 5px;
  border-radius: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
  pointer-events: initial;
  i {
    margin: 0;
  }
`;

export const FullscreenButton = styled(LegacyWBIcon).attrs({
  name: 'fullscreen',
  role: 'button',
  tabindex: 0,
})``;

export const DevQueryIcon = styled(Icon).attrs({name: 'chart area'})``;

export const DevQueryPopupContent = styled.div`
  max-height: 400;
  max-width: 1200;
  overflow: auto;
  font-size: 14;
  white-space: nowrap;
`;

export const DevQueryPopupLabel = styled.span`
  font-weight: bold;
`;

const gradient = keyframes`
  { 
    0%   { background-position: 0 0; }
    100% { background-position: -200% 0; }
  }
`;

export const Panel2SizeBoundary = styled.div`
  width: 100%;
  height: 100%;
`;

export const Panel2FullScreen = styled.div`
  height: calc(90vh - 73px);
  width: calc(90vw - 73px);
  position: relative;
  overflow: hidden;
  display: flex;
  justifycontent: stretch;
  alignitems: stretch;
`;

export const Panel2FullScreenMain = styled.div`
  flex: 1 1 auto;
`;

export const Panel2FullScreenConfig = styled.div`
  flex: 1 1 auto;
`;

export const Panel2LoaderStyle = styled.div`
  background: repeating-linear-gradient(to right, #fff 0%, #ddd 50%, #fff 100%);
  width: calc(100% - 6px);
  height: calc(100% - 6px);
  background-size: 200% auto;
  background-position: 0 100%;
  animation: ${gradient} 2s infinite;
  animation-fill-mode: forwards;
  animation-timing-function: linear;
  border-radius: 0.3em;
  margin: 3px 0px 0px 3px;
`;

export const GrowToParent = styled.div`
  flex: 1 1 auto;
  width: 100%;
  height: 100%;
`;

export const FullScreenModal = styled(Modal.Content)`
  height: calc(90vh - 73px);
  width: calc(90vw - 73px);
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: stretch;
  alignitems: stretch;
`;
